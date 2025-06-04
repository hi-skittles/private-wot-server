import BigWorld
import service_utils
print "Importing pika"
import traceback
traceback.print_stack()
import pika
import pickle
import bwdebug
import logging
from BWPikaConnection import BWPikaConnection

class AMQPExample( BigWorld.Service ):
	QUEUE_NAME = "AccountAdmin"
	EXCHANGE = ""
	
	def __init__( self ):
		# Limit logging from pika to warnings
		pikaLogger = logging.getLogger( "pika" )
		pikaLogger.setLevel( logging.INFO )

		self.connection = None
		self.channel = None
		
		def _validateCreateEntity( params ):
			return "name" in params and \
				isinstance( params["name"], unicode ) and \
				"position" in params and \
				isinstance( params["position"], tuple ) and \
				len( params["position"] ) == 3

		self.methodCalls = {
			"createEntity": 
				{ 
					"validate": _validateCreateEntity, 
					"call": lambda params: self.createEntity( **params )
				}
			}
		
		BigWorld.fetchDataSection( "server/config/services/amqp_example.xml",
			self.onConfigLoaded )
		
	def onConfigLoaded( self, dataSection ):
		if dataSection == None:
			return

		if not dataSection.readBool( "enabled", False ):
			return

		params = {}
		if dataSection.has_key( "username" ) and \
				dataSection.has_key( "password" ):
			params[ 'credentials' ] = pika.PlainCredentials(
					dataSection.readString( "username" ),
					dataSection.readString( "password" ),
					dataSection.readBool( "eraseOnConnect", False ) )
		
		# ssl (bool) and ssl_options (dict) are not in the list as additional
		# validation and fetching is required to handle these
		options = {'host' : str, 'port' : int, 'virtual_host' : str,
			'channel_max' : int , 'frame_max' : int, 'heartbeat_interval' : int,
			'connection_attempts' : int, 'retry_delay' : float ,
			'socket_timeout' : float, 'locale' : str,
			'backpressure_detection' : bool }

		for key, type in options.iteritems():
			if dataSection.has_key( key ):
				if type == str:
					params[ key ] = dataSection.readString( key )
				elif type == int:
					params[ key ] = dataSection.readInt( key )
				elif type == float:
					params[ key ] = dataSection.readFloat( key )

		parameters = pika.ConnectionParameters( **params )
		self.connection = BWPikaConnection( parameters, self.onConnected )

	def onDestroy( self ):
		connection.close()
		self.connection = None
		self.channel = None

	def createEntity( self, name, position ):
		params = {
			'playerName' : name,
			'position' : position,
			'direction' : (0, 0, 0),
		}

		avatar = BigWorld.createBaseAnywhere( 'Avatar', params )
		return avatar.id

	def onConnected( self, connection ):
		"""Called when we are fully connected to RabbitMQ"""
		connection.channel( self.onChannelOpen )

	def onChannelOpen( self, newChannel ):
		"""Called when our channel has opened"""
		self.channel = newChannel
		self.channel.queue_declare( queue = self.QUEUE_NAME, durable = True, \
			exclusive = False, auto_delete = False, \
			callback = self.onQueueDeclared )

	def onQueueDeclared( self, frame ):
		"""Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
		self.channel.basic_consume( self.onMessageReceived, queue=self.QUEUE_NAME )

	def onMessageReceived( self, channel, method, header, body ):
		"""Called when we receive a message from RabbitMQ"""
		try:
			rpcData = pickle.loads( body )
			
			if not isinstance( rpcData, tuple ) or len( rpcData ) != 2:
				raise ValueError, "Invalid RPC data"

			if rpcData[0] not in self.methodCalls:
				raise ValueError, "Unable to find method"

			rpcMethod = self.methodCalls[ rpcData[ 0 ] ]

			if "validate" in rpcMethod and \
				not rpcMethod[ "validate" ]( rpcData[ 1 ] ):
				raise ValueError, "Failed to validate call"

			response = rpcMethod[ "call" ]( rpcData[ 1 ] )

			channel.basic_publish( self.EXCHANGE, 
				routing_key = header.reply_to,
				properties = pika.BasicProperties( correlation_id = header.correlation_id ),
				body = pickle.dumps( response ) )
			channel.basic_ack( delivery_tag = method.delivery_tag )
			
		except Exception as e:
			channel.basic_publish( self.EXCHANGE, 
				routing_key = header.reply_to,
				properties = pika.BasicProperties( correlation_id = header.correlation_id ),
				body = pickle.dumps( e ) )
			channel.basic_ack( delivery_tag = method.delivery_tag )
			return

service_utils.addStandardWatchers( AMQPExample )
