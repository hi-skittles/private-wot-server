import BigWorld
from SpaceRecording import SPACE_DATA_RECORDER_FRAGMENT, recordersForSpaceID
from cPickle import dumps

import logging
log = logging.getLogger( "Recorder" ) 


class Recorder( object ):
	"""
	This is a mix-in class for cell entities for handling space recording.

	The __init__() method of subclasses MUST call Recorder.__init__().

	If the onDestroy() callback method is implemented, subclasses MUST call
	Recorder.onDestroy().
	"""

	def __init__( self ):
		"""
		Constructor.

		This should be called from any subclass's __init__ method.
		"""
		self.base.onCellCreated( self.spaceID )

		# Remove any leftover recording space data if the space was auto-loaded.
		BigWorld.delSpaceDataForKey( self.spaceID, 
			SPACE_DATA_RECORDER_FRAGMENT )


	def startRecording( self, recordingLabel, shouldRecordAoIEvents ):
		"""
		This method starts the recording collection.

		@param recordingLabel 	The label (filename) for the recording.
		"""
		BigWorld.startRecording( self.spaceID, recordingLabel, 
			shouldRecordAoIEvents )


	def onGetSpaceRecorders( self, spaceRecorders ):
		"""
		This method is called in response to a request to start recording, with
		the space recorder service fragment to use.

		@param spaceRecorders 	The list of mailboxes to space recorder service
								fragments to broadcast tick data to.
		"""
		spaceRecorders = filter( lambda x: x is not None, spaceRecorders )

		BigWorld.setSpaceData( self.spaceID, SPACE_DATA_RECORDER_FRAGMENT,
			dumps( list( spaceRecorders ) ) )


	def onLoseSpaceRecorder( self, lostRecorder ):
		"""
		This method is called when a service fragment becomes unavailable that
		was being used to broadcast recorded tick data for this space.

		@param lostRecorder 	The mailbox to the service fragment that was
								lost.
		"""

		recorders = recordersForSpaceID( self.spaceID )

		log.debug( "%s(Recorder).onLoseSpaceRecorder: Lost %r",
			self.__class__.__name__, lostRecorder )

		recorders = filter( lambda x: x.id != lostRecorder.id, recorders)

		if not recorders:
			log.debug( "%s(Recorder).onLoseSpaceRecorder: "
					"No more recorders, stopping recording", 
				self.__class__.__name__ )
			BigWorld.stopRecording( self.spaceID )
			BigWorld.delSpaceDataForKey( self.spaceID, 
				SPACE_DATA_RECORDER_FRAGMENT )

		else:
			BigWorld.setSpaceData( self.spaceID, SPACE_DATA_RECORDER_FRAGMENT,
				dumps( recorders ) )


	def onDestroy( self ):
		"""
		The onDestroy callback. This should be called from any onDestroy() 
		overridden in subclasses.
		"""

		try:
			BigWorld.stopRecording( self.spaceID )
			BigWorld.delSpaceDataForKey( self.spaceID, 
				SPACE_DATA_RECORDER_FRAGMENT )
			log.debug( "%s(Recorder).onDestroy: Recording stopped", 
				self.__class__.__name__ )
		except:
			# We weren't recording, so we're OK.
			pass
			

# Recorder.py
