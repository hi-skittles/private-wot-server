import logging
import socket
import time
import BigWorld
import functools
import BackgroundTask
from pika.adapters import base_connection
import pika

LOGGER = logging.getLogger( __name__ )

class BWPikaIOLoop( object ):
	READ = base_connection.BaseConnection.READ
	WRITE = base_connection.BaseConnection.WRITE

	def __init__( self, handler ):
		self.handler = handler
		self.state = 0
		
	def callbackHandler( self, fd, event ):
		self.handler( fd, event )

	def update_handler( self, fileno, events ):
		wantsRead = (events & self.READ)
		hasRead = (self.state & self.READ)
		
		if wantsRead and not hasRead:
			BigWorld.registerFileDescriptor( fileno,
					lambda fd: self.handler( fd, self.READ ), "AMQP" )
		elif not wantsRead and hasRead:
			BigWorld.deregisterFileDescriptor( fileno )

		wantsWrite = (events & self.WRITE)
		hasWrite = (self.state & self.WRITE)

		if wantsWrite and not hasWrite:
			BigWorld.registerWriteFileDescriptor( fileno,
					lambda fd: self.handler( fd, self.WRITE ), "AMQP" )
		elif not wantsWrite and hasWrite:
			BigWorld.deregisterWriteFileDescriptor( fileno )

		self.state = events

	def add_timeout( self, deadline, callback_method) :
		return BigWorld.addTimer( 
			lambda id, userArg: callback_method(),
			deadline )

	def remove_timeout( self, timeout_id ):
		return BigWorld.delTimer( timeout_id )
		
	def stop( self ):
		pass


class BWPikaConnection( base_connection.BaseConnection ):
	def _adapter_connect( self ):
		"""Connect to the RabbitMQ broker"""
		LOGGER.debug( 'Connecting the adapter to the remote host' )
		if BigWorld.hasStarted():
			LOGGER.warning( 'Connection to AMQP server done while server is '
						'running, this could potentialy block' )
		super( BWPikaConnection, self )._adapter_connect()
		self.ioloop = BWPikaIOLoop( self._handle_events )
		return True


	def _adapter_disconnect( self ):
		hasRead = (self.event_state & self.READ)
		hasWrite = (self.event_state & self.WRITE)
		fileno = self.socket.fileno()
		if hasRead:
			BigWorld.deregisterFileDescriptor( fileno )
		if hasWrite:
			BigWorld.deregisterWriteFileDescriptor( fileno )
		super( BWPikaConnection, self )._adapter_disconnect()



class BWBGPikaConnection( base_connection.BaseConnection, 
		BackgroundTask.BackgroundTask ):
	"""Pika Connection that handles the initial connecting
	in a background thread"""

	LOGGER.debug ("BWBGPikaConnection: starting BG Task Manager")
	
	bgMgr = BackgroundTask.Manager( "BW Pika Connection Tasks" )
	bgMgr.startThreads( 1 )

	
	def __init__( self, 
			parameters = None, 
			on_open_callback = None, 
			on_open_error_callback = None, 
			on_close_callback = None ):

		self.isConnecting = False
		self.disconnectPending = False
		self.closeRequested = None
		self.error = None
		self.ioloop = None

		super( BWBGPikaConnection, self ).__init__( 
					parameters, on_open_callback, 
					on_open_error_callback, on_close_callback )
		BackgroundTask.BackgroundTask.__init__( "BWGBPikaConnection" )

    
	def doBackgroundTask( self, mgr, threadData ):
		super( BWBGPikaConnection, self ).connect()

    
	def _on_connected( self ):
		"""Process connection results in the main thread"""
		BWBGPikaConnection.bgMgr.addMainThreadTask( self )

    
	def _handleFailedConnect( self ):
		# copied from Connection.py's connect()
		self.callbacks.process( 0, self.ON_CONNECTION_ERROR, self, self )
		self.remaining_connection_attempts = self.params.connection_attempts
		self._set_connection_state( self.CONNECTION_CLOSED )

    
	def doMainThreadTask( self, mgr ):
		"""Finished connecting in bg thread"""
		self.isConnecting = False

		if self.error:
			self._handleFailedConnect()
			return None

		if self.closeRequested:
			super( BWBGPikaConnection, self ).close( 
				self.closeRequested[0], self.closeRequested[1] )

		elif self.disconnectPending:
			self._adapter_disconnect()

		else:
			self.ioloop = BWPikaIOLoop( self._handle_events )
			super( BWBGPikaConnection, self )._on_connected()

    
	def _adapter_connect( self ):
		"""Called from connect in the bg thread"""

		if not self.isConnecting:
			raise "Internal error: _adapter_connect called in main thread!"

		LOGGER.debug ("BWBGPikaConnection: Connecting the "
						"adapter to the remote host" )
		# Return OK to Connection and circumvent re-try logic.
		self.error = not super( BWBGPikaConnection, self )._adapter_connect()
		return True

    
	def _adapter_disconnect(self):
		"""Disconnect happened, clean up"""
		
		if self.isConnecting:
			self.disconnectPending = True
			return
		
		if self.ioloop:
			hasRead = self.event_state & self.READ
			hasWrite = self.event_state & self.WRITE
			fileno = self.socket.fileno()
			if hasRead:
				BigWorld.deregisterFileDescriptor( fileno )
			if hasWrite:
				BigWorld.deregisterWriteFileDescriptor( fileno )
			
		# fix Pika"s "we're screwed so I'll just raise an exception" 
		# handling of authentication error. That does not work well
		# with reactors since there's nobody to catch it.
		try:
			super( BWBGPikaConnection, self )._adapter_disconnect()
		except pika.exceptions.ProbableAuthenticationError:
			self.closing = ( 0, "Probable authentication error" )
            

	def connect( self ):
		"""Connect called from __init__ or directly"""
		
		if self.isConnecting:
			# connect requested while bg thread active, ignore
			return
		
		self.isConnecting = True
	
		BWBGPikaConnection.bgMgr.addBackgroundTask( self )

    
	def close( self, reply_code = 200, reply_text = "Normal shutdown" ):
		"""Close requested"""

		if self.isConnecting:
			self.closeRequested = (reply_code, reply_text)
			return

		if self.ioloop:
			super( BWBGPikaConnection, self ).close( reply_code, reply_text )
		else:
			self._adapter_disconnect()


