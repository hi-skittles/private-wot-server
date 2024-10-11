import BigWorld

from bwdecorators import eventListener, functionWatcher, \
	functionWatcherParameter
import random

from functools import partial

import logging
log = logging.getLogger( "Recorder" )


# TODO: make this configurable
BACKUP_CHECK_PERIOD = 1.0


class Recorder( object ):
	"""
	Mix-in class for implementing functionality for talking to a SpaceRecorder
	service.

	Derived entity types should have their .def implement the Recorder
	interface as well as deriving from this class.
	"""

	def onCellCreated( self, spaceID ):
		"""
		This method is called by the cell entity to pass through the space ID.

		This is normally called by the corresponding cell mix-in Recorder
		class on construction.

		@param spaceID 	The space ID.
		"""
		self.spaceID = spaceID


	def setUpRecording( self, label, shouldRecordAoIEvents, metaDataList ):
		"""
		This method sets up space recording with a SpaceRecorder service.

		@param label 					The label to call the recording.
		@param shouldRecordAoIEvents 	Whether to record AoI events.
		@param metaDataList 			A list of meta-data key-value pairs.
		"""

		log.info( "%s(Recorder).setUpRecording: Started for space %d label=%r",
			self.__class__.__name__, self.spaceID, label )

		if self.spaceID == 0:
			log.error( "%s(Recorder).setUpRecording: "
					"Invalid space ID. Either no cell entity was created, or "
					"onCellCreated() on the base was not called because "
					"Recorder.__init__() was not called from the cell entity.",
				self.__class__.__name__ )
			raise ValueError( "No space ID set yet." )

		if self.recordingService is not None:
			log.error( "%s(Recorder).setUpRecording: "
					"Recording already exists for this space(%d)",
				self.__class__.__name__, self.spaceID )
			raise ValueError( "Recording already exists" )

		self.recordingService = BigWorld.services.get( "SpaceRecorder" )

		if self.recordingService is None:
			log.error( "%s(Recorder).setUpRecording: "
					"No SpaceRecorder fragments available",
				self.__class_.__name__ )
			raise ValueError( "No SpaceRecorder fragments available" )

		self.recordingName = label

		log.debug( "%s(Recorder).setUpRecording: Using service %r", 
				self.__class__.__name__, self.recordingService )

		self.allocateNewBackup()

		primaryDeferred = self.recordingService.startRecording( self.spaceID, 
			label, metaDataList, self )

		primaryDeferred.addCallbacks( 
			partial( self.onRecordingServiceStarted, shouldRecordAoIEvents ),
			self.onRecordingServiceFailedToStart )

		return primaryDeferred


	def onRecordingServiceStarted( self, shouldRecordAoIEvents, args ):
		"""
		This method is called when the recording service has started
		successfully.
		"""
		recorders = [self.recordingService]
		if self.backupService:
			recorders.append( self.backupService )

		self.cell.onGetSpaceRecorders( recorders )
		self.cell.startRecording( self.recordingName, 
			shouldRecordAoIEvents )



	def onRecordingServiceFailedToStart( self, failure ):
		"""
		This method is called when the recording service failed to start.
		"""
		log.error( "%s(Recorder).setUpRecording: "
				"Got error from SpaceRecorder service, "
				"recording not started: %s",
			self.__class__.__name__, failure.getErrorMessage() )
		self.recordingService = None
		self.recordingName = ""

		self.stopBackup()

		return failure


	def tearDownRecording( self ):
		"""
		This method tears down the space recording.
		"""
		self.recordingName = ""

		self.stopBackup()

		if self.recordingService:
			deferred = self.recordingService.stopRecording( self.spaceID )

			if hasattr( self, "cell" ):
				self.cell.onLoseSpaceRecorder( self.recordingService )

			self.recordingService = None

			return deferred

		return tuple()


	def stopBackup( self ):
		"""
		This method cleans up a backup service, if it exists.
		"""
		if self.backupService:
			self.backupService.stopRecording( self.spaceID )

			if hasattr( self, "cell" ):
				self.cell.onLoseSpaceRecorder( self.backupService )

			self.backupService = None

		self.enableBackupSearch( False )


	def onServiceAppDeath( self, addr ):
		"""
		This method handles a ServiceApp death.

		@param addr 	The address of the dead ServiceApp.
		"""
		if (self.recordingService is not None) and \
				(self.recordingService.address == addr):
			self.handleRecordingServiceDeath()

		elif (self.backupService is not None) and \
				self.backupService.address == addr:
			self.allocateNewBackup()


	def onServiceDestroyed( self, mailbox ):
		"""
		This method handles the destruction of a service that was responsible
		for our recording or recording backup.

		@param mailbox 	The mailbox of the service that was stopped.
		"""
		if mailbox.id == self.recordingService.id:
			self.handleRecordingServiceDeath()
		elif mailbox.id == self.backupService.id:
			self.handleBackupServiceDeath()
		else:
			log.error( "%s(Recorder).onServiceDestroyed: Not our recorder: %r", 
				mailbox )


	def handleRecordingServiceDeath( self ):
		"""
		This method handles the death of our primary recording service, and
		attempts to switch over to a backup.
		"""

		self.cell.onLoseSpaceRecorder( self.recordingService )
		self.recordingService = None

		if not self.backupService:
			log.error( "%s(Recorder).handleRecordingServiceDeath: "
					"No backups available, recording is stopped",
				self.__class__.__name__ )
			self.recordingName = ""
			return

		self.recordingService = self.backupService
		self.backupService = None
		self.allocateNewBackup()

		deferred = self.recordingService.promote( self.spaceID )
		deferred.addErrback( self.onPromotionFailed )


	def onPromotionFailed( self, failure ):
		"""
		This errback handles when a backup promotion fails.
		"""
		log.error( "%s(Recorder).handleRecordingServiceDeath: "
				"Could not promote backup, tearing down recording : %s",
			self.__class__.__name__, failure.getErrorMessage() )
		self.tearDownRecording()


	def handleBackupServiceDeath( self ):
		"""
		This method handles a backup service death.
		"""

		self.cell.onLoseSpaceRecorder( self.backupService )
		self.backupService = None

		if self.recordingService:
			self.recordingService.updateBackups( self.spaceID, [] )

			# We don't call allocateNewBackup() here because if we may receive
			# this method invocation before the service fragment map update is
			# received, so defer backup allocation.
			self.enableBackupSearch()


	def allocateNewBackup( self ):
		"""
		This method allocates a new backup service for writing the replay.
		"""
		if self.backupService:
			self.cell.onLoseSpaceRecorder( self.backupService )

		self.backupService = self.chooseBackupForRecorderFragment()

		if not self.backupService:
			self.enableBackupSearch()
			return

		deferred = self.backupService.startBackup( self.spaceID, 
			self.recordingName, self )

		deferred.addCallbacks( self.onGetBackup, self.onGetBackupFailed )

		return deferred


	def onGetBackup( self, returnValues ):
		"""
		This is called when the backup recording service has successfully started.
		"""
		if not self.recordingService:
			self.stopBackup()
			return

		self.recordingService.updateBackups( self.spaceID, 
			[self.backupService] )

		self.cell.onGetSpaceRecorders( 
			[self.recordingService, self.backupService] )


	def onGetBackupFailed( self, failure ):
		"""
		This is called when the backup recording service has failed to start.
		"""
		if self.recordingService is None:
			return

		log.error( "%s(Recorder).allocateNewBackup: "
				"Failed to start backup on %r", 
			self.__class__.__name__, self.backupService )
		self.backupService = None
		self.enableBackupSearch()


	def enableBackupSearch( self, shouldEnable = True ):
		"""
		This method enables or disables the backup search timer.
		"""
		if (shouldEnable and (self.backupSearchTimer != 0)) or \
				(not shouldEnable and (self.backupSearchTimer == 0)):
			return

		if shouldEnable:
			self.backupSearchTimer = self.addTimer( 0, BACKUP_CHECK_PERIOD )
		else:
			self.delTimer( self.backupSearchTimer )
			self.backupSearchTimer = 0


	def onTimer( self, timerID, arg ):
		"""
		This callback is fired on timer timeouts.

		@param timerID 	The timer ID.
		@param arg 		The user data for this timer.
		"""
		if timerID == self.backupSearchTimer:
			if self.recordingService is None:
				# We've stopped recording, no need to keep searching for a
				# backup.
				self.enableBackupSearch( False )
				return

			self.allocateNewBackup()

			if self.backupService:
				log.debug( "%s(Recorder).onTimer: Found backup, "
						"cancelling timer: %r",
					self.__class__.__name__, self.backupService )
				self.enableBackupSearch( False )


	def chooseBackupForRecorderFragment( self ):
		"""
		This method chooses a backup writer service from the available service
		fragments.

		@param service 	The primary writer service.

		@return a suitable backup service, or None if none exists.
		"""
		backupCandidates = filter( lambda x : x.id != self.recordingService.id, 
				BigWorld.services.allFragmentsFor( "SpaceRecorder" ) )

		if not backupCandidates:
			return None

		return random.choice( backupCandidates )


	def onLoseCell( self ):
		"""
		This method implements the callback when we lose our cell.
		"""
		if self.recordingService:
			self.tearDownRecording()


@eventListener( "onServiceAppDeath" )
def onServiceAppDeath( addr ):
	"""
	Handler for ServiceApp death.
	"""
	for recorder in BigWorld.entities.values():
		if not isinstance( recorder, Recorder ):
			continue
		recorder.onServiceAppDeath( addr )


@functionWatcher( "command/setUpRecording", BigWorld.EXPOSE_BASE_APPS, 
	"Set up recording" )
@functionWatcherParameter( int, "Space ID" )
@functionWatcherParameter( str, "Recording resource path" )
@functionWatcherParameter( bool, "Should record AoI events (true/false)" )
@functionWatcherParameter( str, "Meta-data (format: key=value[;key=value ...])" )
def setUpRecording( spaceID, recordingPath, shouldRecordAoIEvents,
		metaData ):
	"""
	This is a function watcher that sets up recording.

	@param spaceID 			The space ID.
	@param recordingPath 	The recording resource path.
	@param shouldRecordAoIEvents
							If True, AoI entry/exit events for each player will
							be recorded.
	@param metaData			A string of meta-data key-value pairs. The string
							format are pairs delimited by semi-colons, with
							each individual key-value pair separated by an
							equals sign.
	"""
	def callback( args ):
		return "Started recording for space {:d} at {}".format(
				spaceID, recordingPath )

	def errback( failure ):
		return formatErrMsg( failure.getErrorMessage() )

	def formatErrMsg( msg ):
		return "Failed to start recording for space {:d} at {}: {}".format(
				spaceID, recordingPath, msg )

	recorders = [e for e in BigWorld.entities.values()
		if isinstance( e, Recorder ) and (e.spaceID == spaceID)]

	if not recorders:
		return formatErrMsg( "Space has no recorders" )

	metaDataList = []
	if metaData:
		for keyValuePair in metaData.split( ';' ):
			try:
				key, value = keyValuePair.split( '=', 1 )
			except ValueError:
				return formatErrMsg( "Could not parse meta-data string " )

			metaDataList.append( (key, value) )

	try:
		deferred = recorders[0].setUpRecording( recordingPath,
				shouldRecordAoIEvents, metaDataList )
		deferred.addCallbacks( callback, errback )
		return deferred
	except Exception as e:
		return formatErrMsg( e )


@functionWatcher( "command/tearDownRecording", BigWorld.EXPOSE_BASE_APPS, 
	"Tear down recording" )
@functionWatcherParameter( int, "Space ID" )
def tearDownRecording( spaceID ):
	"""
	This is a function watcher that tears down recording.

	@param spaceID 			The space ID.
	"""
	def callback( args ):
		return "Stopped recording for space {:d} at {}".format(
				spaceID, recordingName )

	def errback( failure ):
		return formatErrMsg( failure.getErrorMessage() )

	def formatErrMsg( errMsg ):
		return "Failed to stop recording for space {:d}: {}".format(
				spaceID, errMsg )

	recorders = [e for e in BigWorld.entities.values() 
		if isinstance( e, Recorder ) and (e.spaceID == spaceID)]

	if not recorders:
		return formatErrMsg( "Space has no recorders" )

	recorder = recorders[0]
	recordingName = recorder.recordingName
	try:
		deferred = recorder.tearDownRecording()
		if deferred:
			deferred.addCallbacks( callback, errback )
			return deferred
		else:
			return formatErrMsg( "Space has no recording" )
	except Exception as e:
		return formatErrMsg( e )


@functionWatcher( "command/queryActiveRecordings", BigWorld.EXPOSE_BASE_APPS, 
	"Query active recordings" )
def queryActiveRecordings():
	"""
	This is a function watcher that prints out information about active
	recordings.
	"""

	activeRecorders = [e for e in BigWorld.entities.values()
		if isinstance( e, Recorder ) and (e.recordingService is not None)]

	for recorder in activeRecorders:
		print( "Space {:d} : \"{}\"".format( recorder.spaceID, 
			recorder.recordingName ) )

	return "I have {:d} recordings".format( len( activeRecorders ) )


# Recorder.py
