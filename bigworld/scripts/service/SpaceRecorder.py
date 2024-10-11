import BigWorld
import ResMgr
from service_utils import (ServiceConfig, ServiceConfigOption,
	ServiceConfigFileOption)
from BWTwoWay import BWFileOpenError, BWInvalidArgsError

from twisted.internet import defer

from functools import partial

import logging
log = logging.getLogger( "Recorder" )


class CompressionLevelServiceConfigOption( ServiceConfigOption ):
	"""
	This class is used for handling the compression level configuration option.
	"""
	def __init__( self, initialValue, initialLevelString, optionName = None ):
		"""
		Constructor.
		"""
		ServiceConfigOption.__init__( self, initialValue,
			optionName = optionName,
			converter = self._convertCompressionLevel,
			getter = self._getter )

		self._levelString = initialLevelString


	def _convertCompressionLevel( self, levelString ):
		"""
		This method converts a string compression level description to the
		corresponding numeric value.
		"""
		badLevelException = ValueError(
			"Invalid compressionLevel specified: {}".format( levelString ) )

		if not levelString.startswith( "COMPRESSION_" ):
			raise badLevelException

		try:
			value = getattr( BigWorld, levelString )
			self._levelString = levelString
			return value
		except AttributeError:
			raise badLevelException


	def _getter( self ):
		"""
		This method returns the representation of this object for watcher
		queries.
		"""
		return self._levelString


class SigningKeyServiceConfigOption( ServiceConfigOption ):
	"""
	This class is used for handling the signing key configuration option.
	"""
	def __init__( self, signingKeyPath, optionName = None ):
		"""
		Constructor.
		"""
		initialValue = ResMgr.openSection( signingKeyPath ).asBinary
		self._signingKeyPath = signingKeyPath

		ServiceConfigOption.__init__( self, initialValue,
			optionName = optionName,
			converter = self._convertSigningKeyPath,
			getter = self._getter )


	def _convertSigningKeyPath( self, path ):
		if path == self._signingKeyPath:
			return self.value

		def callback( section ):
			if section is None:
				log.error( "SpaceRecorder.Config.SIGNING_KEY: "
						"Could not find signing key at %s",
					path )
				self._signingKeyPath = ''
				setattr( self.configClass, self.name, '' )
				return
			log.info( "%r.%r: loaded from %s", self.configClass, self.name,
				path )
			setattr( self.configClass, self.name, section.asBinary )

		self._signingKeyPath = path
		BigWorld.fetchDataSection( path, callback )

		# Just return the current value for self-assignment
		return self.value


	def _getter( self ):
		return self._signingKeyPath


class Config( ServiceConfig ):
	"""
	This is the configuration class for SpaceRecorder.
	"""
	class Meta:
		SERVICE_NAME = "SpaceRecorder"

	# Path to config file for self service, relative to the 'res' path.
	CONFIG_PATH = ServiceConfigFileOption(
		'server/config/services/space_recorder.xml' )

	# Whether opening a new file for writing (non-recovery mode) should
	# overwrite an existing file.
	SHOULD_OVERWRITE = False

	# Compression level used for tick data.
	COMPRESSION_LEVEL = CompressionLevelServiceConfigOption(
		BigWorld.COMPRESSION_ZIP_BEST_SPEED,
		"COMPRESSION_ZIP_BEST_SPEED" )

	# Signing key used for replay files.
	SIGNING_KEY = SigningKeyServiceConfigOption( 'server/replay-sign.privkey',
		optionName = "signingKeyPath" )

	NUM_TICKS_TO_SIGN = 10



class BufferedTickData( object ):
	"""
	This class stores the tick blobs and their metadata for a recording backup
	for a tick that have not been known to be written out yet from the primary.
	"""

	def __init__( self ):
		"""
		Constructor.
		"""
		self.blobs = []


	def addBlob( self, numCells, blob ):
		"""
		This method adds a tick data blob, with the associated data.

		@param numCells 	The number of cells present in the space for this
							tick.
		@param blob 		The tick data for a cell in the space.
		"""
		self.blobs.append( (numCells, blob) )


	def apply( self, gameTime, writer ):
		"""
		This method applies the buffered tick data blobs to the given writer.

		@param gameTime 	The game time to apply the tick data for.
		@param writer 		The file writer to write tick data out to.
		"""
		for numCells, blob in self.blobs:
			writer.addTickData( gameTime, numCells, blob )


class Backup( object ):
	"""
	This class stores backup tick data and state required for recovering a
	failed recorder service.
	"""

	def __init__( self, name, spaceID, recorder ):
		"""
		Constructor.

		@param name 		The name of the recording.
		@param spaceID 		The space ID.
		@param recorder 	The recorder base entity to report to.
		"""

		self.name = name
		self.spaceID = spaceID
		self.recorder = recorder
		self.recoveryData = None
		self.tickData = {}


	def cellTickDataWritten( self, gameTime, recoveryData ):
		"""
		This method updates the backup with the latest writer recovery state.

		@param gameTime 		The last game time's tick data that was written
								out.
		@param recoveryData 	The recovery data.
		"""
		self.recoveryData = recoveryData
		self.clearWrittenTickData( gameTime )


	def clearWrittenTickData( self, gameTime ):
		"""
		This method clears tick data that is known to have been written out to
		disk successfully.
		"""
		for tick in list( self.tickData.keys() ):
			if tick <= gameTime:
				del self.tickData[tick]


	def addTickData( self, gameTime, numCells, data ):
		"""
		This method adds fresh tick data that has not yet been written out to
		disk.

		It will either be cleared when we get notification of successful write,
		or it will be used to write out to the file when this backup is
		promoted during recovery.

		@param gameTime 	The game time for this tick.
		@param numCells 	The number of cells in the space for this tick.
		@param data 		The game tick data.
		"""
		bufferedTickData = self.tickData.setdefault( gameTime,
			BufferedTickData() )
		bufferedTickData.addBlob( numCells, data )


	def promoteToRecorderInfo( self ):
		"""
		This method promotes this backup to be the primary recorder.

		"""

		if self.recoveryData is None:
			raise ValueError( "Could not promote to primary, "
				"did not hear from previous primary" )

		log.info( "Backup.promoteToRecorderInfo( space %d ) ",
			self.spaceID )

		recorderInfo = RecorderInfo( self.name, self.spaceID,
			self.recorder,
			recoveryData = self.recoveryData )

		minTick = min( self.tickData.keys() )
		maxTick = max( self.tickData.keys() )

		for tick in range( minTick, maxTick + 1 ):
			self.tickData[tick].apply( tick, recorderInfo.writer )

		return recorderInfo


class RecorderInfo( object ):
	"""
	This class holds together the state required for a primary recorder.
	"""
	def __init__( self, name, spaceID, recorder, recoveryData = None,
			metaData = [] ):
		"""
		Constructor.

		@param name 		The filename of the recording.
		@param spaceID 		The space ID.
		@param recorder 	The Recorder base entity mailbox.
		@param recoveryData	The recovery data, if recovering, otherwise None.
		@param metaData 	The meta-data, as a list of key-value string pairs.
		"""

		if recoveryData is None:
			# Creation mode
			self.writer = BigWorld.createReplayDataFileWriter( name,
				Config.SIGNING_KEY,
				numTicksToSign = Config.NUM_TICKS_TO_SIGN,
				shouldOverwrite = Config.SHOULD_OVERWRITE,
				compressionType = Config.COMPRESSION_LEVEL,
				metaData = dict( metaData ) )
		else:
			# Recovery mode
			self.writer = BigWorld.createReplayDataFileWriter( name,
				Config.SIGNING_KEY,
				recoveryData = recoveryData )

		self.writer.setListener( self.onFileOpenComplete )

		self.spaceID = spaceID
		self.recorder = recorder
		self.backups = []
		self.openDeferred = defer.Deferred()


	def addWriterOpenCallback( self, callback ):
		"""
		This method adds a callback for when the file is opened successfully.

		@param callback 	The callback to add.
		"""
		if self.openDeferred:
			self.openDeferred.addCallback( callback )


	def addWriterOpenErrback( self, errback ):
		"""
		This method adds a error callback for when the file is fails to open.

		@param errback 	The error callback to add.
		"""
		if self.openDeferred:
			self.openDeferred.addErrback( errback )


	def onFileOpenComplete( self, writer, success ):
		"""
		This method is registered as the initial callback, called back when
		file open completes.

		@param writer 	The file writer.
		@param success 	File open success flag.
		"""
		log.debug( "RecorderInfo.onFileOpenComplete: "
				"For space %d => %r: success = %r",
			self.spaceID, writer.resourcePath, success )

		if success:
			self.writer.setListener( self.onFileWriteComplete )
			self.openDeferred.callback( self )
		else:
			log.error( "RecorderInfo.onFileOpenComplete( %s ): "
					"Error opening file: %s",
				self.spaceID, writer.errorString )
			self.openDeferred.errback( self )

		self.openDeferred = None


	def onFileWriteComplete( self, writer, success ):
		"""
		This method is registered as the writer listener callback after the
		file is opened successfully.

		@param writer 	The file writer.
		@param success	File write success flag.
		"""
		if success:
			for backup in self.backups:
				backup.cellTickDataWritten( self.spaceID,
					self.writer.lastTickWritten,
					self.writer.recoveryData )
		else:
			log.error( "RecorderInfo.onFileWriteComplete: "
					"Failure while writing to file (stopping recording): %s",
				writer.errorString );
			self.recorder.tearDownRecording()



class SpaceRecorder( BigWorld.Service ):

	"""
	This service is used to record a space's entity and space data each tick. A
	primary recorder is used to write the tick data to the file, while a
	secondary recorder service is used as a backup, if available, to recover in
	the event the primary recorder fails.
	"""

	def __init__( self ):
		"""
		Constructor.
		"""

		# Writer instances can't be streamed, so this is marked as a temporary
		# property.
		self.writers = {}
		self.backups = {}

		BigWorld.addWatcher( "services/SpaceRecorder/numWriters",
			lambda: len( self.writers ) )

		BigWorld.addWatcher( "services/SpaceRecorder/numBackups",
			lambda: len( self.backups ) )


	def startRecording( self, spaceID, name, metaDataList, recorder ):
		"""
		This method is called when a recording has started for the given space.

		@param spaceID 		The space ID.
		@param name 		The name given to BigWorld.startRecording().
		@param metaDataList	The meta-data as a list of key-value string pairs.
		@param recorder 	The recorder base entity mailbox.
		"""

		if spaceID == 0:
			log.error( "SpaceRecorder.startRecording: "
					"Invalid space ID %d", spaceID )
			return defer.fail( BWInvalidArgsError(
				"Invalid space ID %d" % spaceID ) )

		if spaceID in self.backups:
			log.error( "SpaceRecorder.startRecording: "
					"Already backing up for space %d",
				spaceID )
			return defer.fail( BWInvalidArgsError(
				"Already recording for space %d" % spaceID ) )

		if spaceID in self.writers:
			log.error( "SpaceRecorder.startRecording: "
					"Already recording for space %d",
				spaceID )

			return defer.fail( BWInvalidArgsError(
				"Already recording for space %d" % spaceID ) )

		try:
			self.writers[ spaceID ] = recorderInfo = \
				RecorderInfo( name, spaceID, recorder, metaData = metaDataList )

		except Exception as e:
			log.error( "SpaceRecorder.startRecording: "
					"Failed to open replay file for writing: %s",
				e )

			return defer.fail( BWFileOpenError(
				"Failed to open replay file for writing for space %d: %s" %
					(spaceID, e) ) )

		deferred = defer.Deferred()

		def onWriterOpenSuccess( recorderInfo ):
			log.info( "SpaceRecorder.startRecording: Space %d => %r",
				spaceID, name )

			deferred.callback( tuple() )

		def onWriterOpenFailure( failure ):
			log.error( "SpaceRecorder.startRecording: "
					"Failed to open replay data file writer for space %d "
					"at %r: %s",
				spaceID, recorderInfo.writer.resourcePath,
				recorderInfo.writer.errorString )
			del self.writers[ recorderInfo.spaceID ]

			deferred.errback(
				BWFileOpenError( "Failed to open replay data file "
					"writer: %s" % recorderInfo.writer.errorString ) )

		recorderInfo.addWriterOpenCallback( onWriterOpenSuccess )
		recorderInfo.addWriterOpenErrback( onWriterOpenFailure )

		return deferred


	def startBackup( self, spaceID, name, recorder ):
		"""
		This method starts this service as a backup recorder.

		@param spaceID 		The space ID being recorded.
		@param name 		The file name of the recording.
		@param recorder 	The recorder base entity mailbox.
		"""
		if spaceID == 0:
			log.error( "SpaceRecorder.startRecording: "
					"Invalid space ID %d", spaceID )
			return defer.fail( BWInvalidArgsError(
				"Invalid space ID %d" % spaceID ) )

		if (spaceID in self.backups) or (spaceID in self.writers):
			log.error( "SpaceRecorder.startBackup: "
					"Already recording or backing up for space %d",
				spaceID )
			raise BWInvalidArgsError( "Already recording or " \
					"backing up for space %d" % spaceID )

		log.info( "SpaceRecorder.startBackup: Space %d", spaceID )
		self.backups[spaceID] = Backup(	name, spaceID, recorder )
		return tuple()


	def updateBackups( self, spaceID, backups ):
		"""
		This method updates the backups for a primary writer.

		@param spaceID 	The space ID of the recording.
		@param backups 	A list of mailboxes to be used for sending recovery
						writer state.
		"""
		recorderInfo = self.writers[spaceID]
		recorderInfo.backups = backups
		log.debug( "SpaceRecorder.updateBackups: %d %r", spaceID, backups )


	def cellTickData( self, spaceID, gameTime, numCells, data ):
		"""
		This method adds tick data from a cell in the given space that has
		started recording.

		@param spaceID 		The space ID.
		@param gameTime 	The game time.
		@param numCells 	The total number of cells in the space at this tick.
		@param data 		The data to write.
		"""

		if spaceID in self.writers:
			writer = self.writers[spaceID].writer

			if writer.isFinalising:
				log.warning( "SpaceRecorder.cellTickData: "
						"File writer is being finalised" )
				return

			writer.addTickData( gameTime, numCells, data )

		elif spaceID in self.backups:
			backup = self.backups[spaceID]
			backup.addTickData( gameTime, numCells, data )

		else:
			log.error( "SpaceRecorder.cellTickData: "
					"No recording or backup for space %d exists",
				spaceID )


	def cellTickDataWritten( self, spaceID, gameTime, recoveryData ):
		"""
		This method is called from the primary service to a backup service to
		notify of a successful write of tick data, so that the backup can
		release any copies of that data that it has buffered.

		@param spaceID 			The space ID of the space being recorded.
		@param gameTime 		The last game time that was written out
								successfully.
		@param recoveryData 	The recovery data.
		"""
		try:
			backup = self.backups[spaceID]
			backup.cellTickDataWritten( gameTime, recoveryData )

		except KeyError:
			log.error( "SpaceRecorder.cellTickDataWritten: "
					"No backup for space %d exists",
				spaceID )


	def promote( self, spaceID ):
		"""
		This method promotes a backup recorder service into the primary
		recording service.

		@param spaceID 			The space ID of the space being recorded.
		"""
		if not spaceID in self.backups:
			raise BWInvalidArgsError( "Invalid spaceID %d" % (spaceID) )

		backup = self.backups[spaceID]
		earliestTick = min( backup.tickData.keys() )
		del self.backups[spaceID]

		self.writers[spaceID] = backup.promoteToRecorderInfo()

		return tuple()


	def stopRecording( self, spaceID ):
		"""
		This method is called when the recording has stopped.

		@param spaceID  	The space ID of the recording being stopped.
		"""

		if (not spaceID in self.writers) and (not spaceID in self.backups):
			log.error( "SpaceRecorder.stopRecording: "
					"No recording for space %d exists",
				spaceID )
			return tuple()

		if spaceID in self.backups:
			log.info( "SpaceRecorder.stopRecording: "
					"Stopping backup for space %d",
				spaceID )

			del self.backups[spaceID]
			return tuple()

		try:

			writer = self.writers[ spaceID ].writer

			if writer.errorString:
				log.debug( "SpaceRecorder.stopRecording: "
						"Removing writer for space %d with error: %s",
					spaceID, writer.errorString )

				# Something bad happened, don't finalise.
				del self.writers[ spaceID ]
				return tuple()

			elif writer.isFinalising:
				# Already finalising.
				return tuple()

			log.info( "SpaceRecorder.stopRecording: "
					"Finalising recording for space %d",
				spaceID )

			deferred = defer.Deferred()

			writer.setListener( partial( self.onFinalised, spaceID, deferred ) )
			writer.close()

			return deferred

		except KeyError:
			log.error( "SpaceRecorder.stopRecording: "
					"No recording for space %d exists",
				spaceID )

		return tuple()


	def onFinalised( self, spaceID, deferred, writer, success ):
		"""
		This method is called when a writer for a recording has been finalised.

		@param spaceID 	The space ID of the space being recorded that is now
						having its writer finalised.
		@param writer 	The writer being finalised.
		@param success 	Whether the file writer was successfully finalised.
		"""
		if not writer.isClosed:
			log.debug( "SpaceRecorder.onFinalised: Not closed" )
			return

		if not success:
			msg = "Failed to finalise for path {}: {}".format(
					writer.resourcePath, writer.errorString )
			log.error( "SpaceRecorder.onFinalised: %s", msg )

			deferred.errback( BWFinaliseError( msg ) )
			return

		log.info( "SpaceRecorder.stopRecording: "
				"Stopping recording for space %d",
			spaceID )

		deferred.callback( tuple() )

		del self.writers[ spaceID ]


	def onDestroy( self ):
		"""
		This is called when the space recorder service is stopped.
		"""

		BigWorld.delWatcher( "services/SpaceRecorder/numWriters" )
		BigWorld.delWatcher( "services/SpaceRecorder/numBackups" )
		BigWorld.delWatcher( "services/SpaceRecorder" )

		for recorderInfo in self.writers.values():
			shouldFinalise = (BigWorld.isShuttingDown() or
				(len( recorderInfo.backups ) == 0))

			recorderInfo.writer.close( shouldFinalise )
			recorderInfo.recorder.onServiceDestroyed( self )

		for backup in self.backups.values():
			backup.recorder.onServiceDestroyed( self )


# SpaceRecorder.py

