import BackgroundTask
from service_utils import (ServiceConfig, ServiceConfigOption,
	ServiceConfigFileOption, ServiceConfigPortsOption)
from TwistedWeb import TwistedWeb

from twisted.internet import abstract, defer, interfaces, reactor, task
from twisted.python.failure import Failure
from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.web.static import File
from twisted.web.util import redirectTo

from zope.interface import implements

import BigWorld
import ResMgr

import importlib
import json
import logging
from math import floor
import os
import random
import re
import threading
import time

log = logging.getLogger( __name__ )
log.setLevel( logging.INFO )


_childNotFound = NoResource( "File not found." )


class AddDataException( Exception ): 
	"""
	This exception is raised when the ReplayDataFileReader rejects data from 
	addData().
	"""
	pass


class DelayException( Exception ):
	"""
	This exception is raised when we need to delay sending of tick data due to
	delay constraints.
	"""
	pass

def fileProducerFactory( f ):
	"""
	Decorator for nominating a file producer factory function.
	"""
	Config.FILE_PRODUCER_FACTORY = staticmethod( f )
	return f


class MetaDataDelayProvider( object ):
	"""
	This class is a delay value provider using a specific key's value present
	in meta-data.
	"""
	def __init__( self, metaDataKey ):
		"""
		Constructor.

		@param metaDataKey 		The meta-data key to use for getting the delay
								provider.
		"""
		self._metaDataKey = metaDataKey


	def __call__( self, fileProducer, metaData ):
		"""
		This method provides the delay based on the meta-data key.
		"""
		try:
			return float( metaData.get( self._metaDataKey, 
				Config.DEFAULT_FILE_PRODUCER_FACTORY_READ_DELAY ) )
		except:
			return Config.DEFAULT_FILE_PRODUCER_FACTORY_READ_DELAY


defaultDelayProvider = MetaDataDelayProvider( "delay" )


def defaultFileProducerFactory( request, fileReader, offset ):
	"""
	Default file producer factory function.

	To nominate a different function in code, use the @fileProducerFactory
	decorator. It can also be changed at run-time by setting the
	Config.FILE_PRODUCER_FACTORY option to a qualified function name.

	@param request  	The Twisted web request object.
	@param fileReader 	The file reader object for this request.
	@param offset 		The requested file offset to start from.
	"""

	return FileProducer( request, fileReader, offset,
		defaultDelayProvider )


def fileProducerFactoryOptionConverter( qualifiedFunctionName ):
	"""
	This method converts watcher input and interprets it as a qualified name of
	a function. e.g. some.module.function would be interpreted by importing
	some.module and using function inside the module as the factory function.
	"""
	if not '.' in qualifiedFunctionName:
		raise ValueError( "Invalid module name" )

	moduleName, factoryName = qualifiedFunctionName.rsplit( '.', 1 )
	factoryModule = importlib.import_module( moduleName )
	return staticmethod( getattr( factoryModule, factoryName ) )


def debugLevelConverter( debugLevelString ):
	"""
	Converter for the logging level config option.
	"""
	if debugLevelString not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
		raise ValueError( "Invalid debug level" )

	level = getattr( logging, debugLevelString )
	log.setLevel( level )
	return level


def debugLevelGetter():
	"""
	Getter for the logging level config option.
	"""
	for levelName in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
		if getattr( logging, levelName ) == log.getEffectiveLevel():
			return levelName

	return str( log.getEffectiveLevel() )


class Config( ServiceConfig ):
	"""
	Configuration class for HTTPReplayService.
	"""

	class Meta:
		SERVICE_NAME = 'HTTPReplayService'

		READ_ONLY_OPTIONS = ["CONFIG_PATH", "NETMASK", "PORTS", "CHUNK_SIZE",
			"SEND_BUFFER_SIZE", "CHUNK_EXPIRE_TIME", "FILE_EXPIRE_TIME",
			"REOPEN_WAIT_TIME", "TICK_RATE", "WAIT_READ_TIMEOUT",
			"IDLE_TICK_LIMIT"]


	# Path to config file for self service, relative to the 'res' path.
	CONFIG_PATH = ServiceConfigFileOption(
		'server/config/services/http_replay.xml' )

	# Netmask used to select which network interface to listen on
	NETMASK = ServiceConfigOption( '', optionName = "interface" )

	# List of ports to try to bind to.
	PORTS = ServiceConfigPortsOption( [0] )

	# The resource path of the document root to serve.
	DOCUMENT_ROOT = ""

	# The size of chunks to cache in bytes (64kb). Don't make this smaller than
	# the replay header size.
	CHUNK_SIZE = abstract.FileDescriptor.bufferSize

	# Send amount in bytes, the client will probably receive at 16kb, but use
	# the 64kb buffer size, to allow the other buffers throughout twisted web to
	# work or else you end up with little bits of headers overlapping and making
	# small packets.
	SEND_BUFFER_SIZE = abstract.FileDescriptor.bufferSize

	# The time which it takes for a file chunk to expire in seconds.
	CHUNK_EXPIRE_TIME = 3

	# File expire time must be higher then CHUNK_EXPIRE_TIME.
	FILE_EXPIRE_TIME = 4

	# The number of seconds to wait for no data to be written before attempting
	# to re-open the file.
	REOPEN_WAIT_TIME = 8.0

	# The time in seconds between attempting to send data to clients.
	TICK_RATE = 0.25

	# Number of times to attempt to read from a file before deciding that it
	# has no more data, in seconds.
	WAIT_READ_TIMEOUT = 120.0

	# The number of idle ticks to continue processing without clients and files
	# must be higher then FILE_EXPIRE_TIME*TICK_RATE to allow chunks to expire.
	IDLE_TICK_LIMIT = (FILE_EXPIRE_TIME * TICK_RATE) + 1

	# The file producer factory to use. This takes the Twisted Web Request
	# object, the FileReader and offset. The factory is free to choose its own
	# readDelay parameter value.
	FILE_PRODUCER_FACTORY = ServiceConfigOption(
		staticmethod( defaultFileProducerFactory ),
		converter = fileProducerFactoryOptionConverter )

	# If the FACTORY above is the default make file producer, this value is
	# used to control the default read delay between when data is written to
	# disk and when it is presented to clients.
	# If the FACTORY is changed, this value will not used unless explicitly
	# used by the new factory function.
	DEFAULT_FILE_PRODUCER_FACTORY_READ_DELAY = 0.0

	# The number of bytes the ReplayFileCache will read from a replay file at a
	# time to get the header and meta-data block.
	REPLAY_FILE_CACHE_READ_BLOCK_SIZE = 1024

	# The minimum number of seconds between two successive refreshes of the
	# ReplayFileCache.
	REPLAY_FILE_CACHE_REFRESH_MIN_TIME = 5.0

	# Whether to also match filenames on the top-level, in addition from
	# /replays. This is for backwards compatibility with 2.4 behaviour.
	SHOULD_MATCH_FILENAMES_AT_TOP_LEVEL = False

	# Whitelist pattern for replay files in the recording directory.
	REPLAY_FILE_PATTERN = ServiceConfigOption( re.compile( r'.*' ),
		converter = re.compile,
		getter = lambda: Config.REPLAY_FILE_PATTERN.pattern )

	# Blacklist pattern for replay files in the recording directory. Overrides
	# matches in the whitelist. Hiding dot files prevents the replay file cache
	# from looking at stale NFS file handles.
	REPLAY_FILE_NON_PATTERN = ServiceConfigOption(
		re.compile( r'\..*|.*\.zip$|.*\.7z$|.*\.gz$|.*\.bz2$' ),
		converter = re.compile,
		getter = lambda: Config.REPLAY_FILE_NON_PATTERN.pattern )

	# This sets the debug log level for this service.
	DEBUG_LEVEL = ServiceConfigOption( logging.INFO,
		converter = debugLevelConverter,
		getter = debugLevelGetter )

	# This is used for debugging, and shouldn't be set in production.
	ARTIFICIAL_BAD_DATA_READ_PROBABILITY = 0.0


class ReplayFileReadingTask( BackgroundTask.BackgroundTask ):
	"""
	This task is responsible for periodically running file reading operations
	in the background.
	"""
	def __init__( self, replaySender ):
		"""
		Constructor.

		@param replaySender 	The replay sender instance.
		"""
		self._loopingTask = task.LoopingCall( self.tick )
		self._replaySender = replaySender
		self._isPending = False


	def doBackgroundTask( self, mgr, threadData ):
		"""
		Override from BackgroundTask.
		"""
		self._replaySender.backgroundTick()
		mgr.addMainThreadTask( self )


	def doMainThreadTask( self, mgr ):
		"""
		Override from BackgroundTask.
		"""
		self._replaySender.tick()
		self._isPending = False


	def tick( self ):
		"""
		This is called in the main thread periodically via the LoopingCall.
		"""
		if not self._replaySender.bgTaskMgr:
			self._loopingTask.stop()
			return

		if self._isPending:
			return

		self._replaySender.bgTaskMgr.addBackgroundTask( self )
		self._isPending = True


	def start( self, tickRate ):
		"""
		This method starts the timer for periodic file operations.
		"""
		self._loopingTask.start( tickRate )


	def stop( self ):
		"""
		This method stops the timer for periodic file operations.
		"""
		if self._loopingTask.running:
			self._loopingTask.stop()


class ReplaySender( object ):
	"""
	This class is responsible for broadcasting file data to clients.
	"""

	def __init__( self ):
		"""Constructor."""
		self.activeFiles = {}
		self.clients = []
		self.task = None
		self.isTaskRunning = False
		self.idleTicks = 0
		self.bgTaskMgr = None


	def setup( self, bgTaskMgr ):
		"""
		This method initiates the broadcasting.
		"""
		self.bgTaskMgr = bgTaskMgr
		self.task = ReplayFileReadingTask( self )


	def tearDown( self ):
		"""
		This method cleans up after the service is shut down.
		"""
		self.bgTaskMgr = None
		self.task.stop()
		self.task = None


	def backgroundTick( self ):
		"""
		This method is called periodically to read file data in the background.
		"""
		for fileReader in self.activeFiles.values():
			fileReader.backgroundTick()

	def tick( self ):
		"""
		This method is called periodically to broadcast the data to clients in
		chunks.
		"""

		expireTime = (time.time() - Config.FILE_EXPIRE_TIME)

		for filename, fileReader in list( self.activeFiles.items() ):
			if (fileReader.numClients == 0) and \
					(fileReader.lastUsed < expireTime):
				log.info( "ReplaySender.tick: Expiring file reader for %s",
					filename )
				del self.activeFiles[ filename ]
			else:
				fileReader.tick()

		if self.clients:
			self.idleTicks = 0
		else:
			self.idleTicks += 1

		if (self.idleTicks > Config.IDLE_TICK_LIMIT) and \
				self.isTaskRunning and \
				not self.clients and \
				not self.activeFiles:
			self.isTaskRunning = False
			self.task.stop()
			return

		for producer in self.clients:
			producer.write()


	def removeClient( self, client ):
		"""
		This method removes a client, given the client's producer.

		@param client 	The file producer.
		"""
		try:
			self.clients.remove( client )
		except ValueError:
			pass


	def addClient( self, client ):
		"""
		This method adds a client, given its producer.

		@param client 	The file producer.
		"""

		self.clients.append( client )

		if not self.isTaskRunning:
			# Start task
			self.isTaskRunning = True
			self.task.start( Config.TICK_RATE )


	def openPath( self, path ):
		"""
		This method returns the file reader for the given path. If none exists,
		a new FileReader is created. File readers expire after not being used
		for a time, see Config.FILE_EXPIRE_TIME.

		@param path 	The file reader.
		"""

		if path in self.activeFiles:
			return self.activeFiles[path]

		fileReader = FileReader( path )
		self.activeFiles[path] = fileReader
		return fileReader


# Singleton instance of ReplaySender
_replaySender = ReplaySender()


class Chunk( object ):
	"""
	This class is represents a cached fixed-size block of a file. The Chunk
	object loads as much data is available from the file at construction.

	@attribute index 	The chunk index assigned to this chunk.
	@attribute data 	The chunk data. Use getData() to retrieve the data
						instead of accessing data directly.
	@attribute lastUsed The time this object was last accessed for reading.

	@see Config.CHUNK_SIZE
	"""

	def __init__( self, fileOffset ):
		"""
		Constructor.

		Loads a chunk from the given file. The file is divided into
		Config.CHUNK_SIZE-sized chunks, each chunk is addressed by a chunk
		index.

		@param index 	The file offset of the start of the chunk.
		@param f 		The file to read from.
		"""
		self.fileOffset = fileOffset
		self.data = ""
		self.lastUsed = None
		self.lastRead = time.time()


	def loadMore( self, f ):
		"""
		This method loads more data from the file, up to Config.CHUNK_SIZE
		bytes.

		@param f 	The file to read from.

		@return 	The amount of new data read.
		"""
		if self.isComplete:
			return

		f.seek( self.fileOffset + len( self.data ), 0 )
		chunk = f.read( Config.CHUNK_SIZE - len( self.data ) )
		if chunk:
			self.lastRead = time.time()
			self.data += chunk

		return len( chunk )


	def scrub( self, offset ):
		"""
		This method is used to scrub known bad data from a chunk in the cache,
		forcing it to be re-read in the next background tick.

		This is useful when we have unreliable network filesystems that decide
		to supply zeroes near the end-of-file rather than reporting a short
		count for read operations.
		"""
		self.data = self.data[:offset]


	def getData( self, start, length ):
		"""
		This method returns the data read from the file, using the given chunk
		offset and length.

		@param start 	The start of the data to retrieve, as a byte offset
						from the start of this chunk.
		@param length 	The length of the data to request for retrieval.

		@return 		The available data within the given range, or None if
						no data in the given range is available. The returned
						data may be shorter than the requested length,
						depending on proximity to the chunk boundary.
		"""
		self.lastUsed = time.time()

		if start >= len( self.data ):
			return None

		return self.data[ start : start + length ]

	@property
	def isComplete( self ):
		"""
		This property returns whether the data read for this chunk is complete.
		"""
		return len( self.data ) == Config.CHUNK_SIZE


class FileReader( object ):
	"""
	This class reads data from a file, caching the read data into fixed-size
	chunks.
	"""

	def __init__( self, path ):
		"""
		Constructor.

		@param path 	The path to the file to open.
		"""
		self.path = path
		self.cache = {}
		self.lastRead = None
		self.lastUsed = time.time()
		self.f = None
		self.stat = None
		self.numClients = 0


	def openFile( self ):
		"""
		This method opens (or re-opens) the file for reading.
		"""
		if self.f:
			self.f.close()

		self.f = open( self.path, 'rb' )
		self.lastRead = time.time()

	def name( self ):
		"""
		Accessor for the file path.
		"""
		return self.f.name


	def read( self, offset, length ):
		"""
		This method reads data from the given file offset with the given
		length. The returned data may be shorter than the requested length.

		@param offset 	The file offset to read from.
		@param length 	The requested length of the data.

		@return 		The data from the file. This data will be cached for
						a time (see Config.CHUNK_EXPIRE_TIME) before being
						released from memory.
		"""

		self.lastUsed = time.time()

		chunkIndex = offset // Config.CHUNK_SIZE
		chunkOffset = offset % Config.CHUNK_SIZE

		chunk = None
		if chunkIndex in self.cache:
			chunk = self.cache[ chunkIndex ]
		else:
			log.debug( "FileReader( %s ).read: "
					"Adding chunk index %d (offset = %d)",
				self.path, chunkIndex, chunkIndex * Config.CHUNK_SIZE )
			chunk = self.cache[ chunkIndex ] = \
				Chunk( chunkIndex * Config.CHUNK_SIZE )

		return chunk.getData( chunkOffset, length )


	def scrub( self, offset ):
		"""
		This method scrubs data from an offset to the end.

		@param offset 	The offset to scrub from.
		"""
		startIndex = offset // Config.CHUNK_SIZE
		startOffset = offset % Config.CHUNK_SIZE
		endIndex = startIndex

		try:
			chunk = self.cache[ startIndex ]
		except KeyError:
			return

		chunk.scrub( startOffset )

		for endIndex in [k for k in self.cache.keys() if k > startIndex]:
			del self.cache[endIndex]

		log.debug( "FileReader( %s ).scrub: offset = %d, chunk index %d to %d",
			self.path, offset, startIndex, endIndex )


	def backgroundTick( self ):
		"""
		This method processes file reading tasks in the background thread.
		"""
		if self.f is None:
			self.openFile()

		self.stat = os.fstat( self.f.fileno() )

		lastChunkIndex = None
		lastChunk = None
		lastChunkRead = 0

		totalAmountRead = 0

		for index, chunk in self.cache.items():
			amountRead = chunk.loadMore( self.f )
			if amountRead is not None:
				totalAmountRead += amountRead

		if totalAmountRead:
			self.lastRead = time.time()

		elif ((time.time() - self.lastRead) >
					Config.REOPEN_WAIT_TIME):
			# Work-around for network file systems
			log.info( "FileReader.tick: Re-opening file path: %r",
				self.path )
			self.openFile()


	def tick( self ):
		"""
		This method processes file readers and producers to clients.
		"""
		if not self.cache:
			return

		lastChunkIndex = None
		lastChunk = None
		expireTime = time.time() - Config.CHUNK_EXPIRE_TIME

		for index, chunk in list( self.cache.items() ):
			if (chunk.lastUsed is not None) and (chunk.lastUsed < expireTime):
				log.debug( "FileReader( %s ).tick: "
						"Expiring chunk at index %d (offset = %d)",
					self.path, index, index * Config.CHUNK_SIZE )
				del self.cache[index]

			elif (lastChunkIndex is None) or (index > lastChunkIndex):
				lastChunkIndex = index
				lastChunk = chunk

		if lastChunk is not None and \
				lastChunk.isComplete and \
				(((lastChunkIndex + 1) * Config.CHUNK_SIZE) < 
					self.stat.st_size):
			log.debug( "FileReader( %s ).tick: "
					"Adding chunk after last chunk at index %d (offset = %d)",
				self.path,
				lastChunkIndex + 1,
				(lastChunkIndex + 1) * Config.CHUNK_SIZE )

			self.cache[lastChunkIndex + 1] = \
				Chunk( (lastChunkIndex + 1) * Config.CHUNK_SIZE )


class FileProducer( object ) :
	"""
	This class produces file data for a web request.
	"""
	implements( interfaces.IPushProducer )

	def __init__( self, request, fileReader, offset, 
			readDelayProvider = defaultDelayProvider ):
		"""
		Constructor.

		@param request 				The request to serve file data for.
		@param fileReader 			The file reader to read data from.
		@param offset 				The initial file offset to read from.
		@param readDelayProvider	The read delay provider to use. This is an
									object that is callable with this object
									and the meta-data dictionary as arguments,
									called when meta-data is read.
		"""
		self.request = request
		self.fileReader = fileReader
		self.fileReader.numClients += 1
		self.offset = offset
		self.sendBuffer = '' 	# This is used to hold data read from the file
								# system that hasn't been verified by the
								# reader yet.
		self.readDelay = None 	# Initially None, will be set when meta-data
								# has been read.
		self.readDelayProvider = readDelayProvider
		self.isPaused = True
		# Non-validating reader, decompression off.
		self.replayFileReader = BigWorld.ReplayDataFileReader( "", False )
		self.replayFileReader.listener = self
		self.pauseStartTime = None
		self.lastPauseDuration = 0.0
		self.lastWriteTime = None
		self.lastReadTime = None
		self.lastGoodReadTime = None

		log.info( "FileProducer.__init__: Started streaming %s to %s:%d",
			fileReader.path,
			self.request.client.host, self.request.client.port )


	def onReplayDataFileReaderMetaData( self, reader, metaData ):
		"""
		Callback from the replay file reader when meta-data has been read.
		"""
		self.readDelay = self.readDelayProvider( self, metaData )


	def onReplayDataFileReaderTickData( self, reader, gameTime, isCompressed,
			data ):
		"""
		Callback from the replay file reader when tick data has been read.
		"""

		now = time.time()

		if not self.readDelay:
			return

		numSecondsRead = (reader.numTicksRead /
			float( reader.header.gameUpdateFrequency ))
		
		maxTickIndexToSend = int( (now - self.readDelay - reader.header.timestamp) *
			reader.header.gameUpdateFrequency )

		# TODO: We don't currently delay the very first frame due to when 
		# ReplayDataFileReader calls back to here, it's already considered the
		# first tick to have been read. Subsequent ticks will still be delayed.

		if (gameTime - reader.firstGameTime) >= maxTickIndexToSend:
			log.debug( "FileProducer.onReplayDataFileReaderTickData: "
					"Read gameTime = %d, tickIndex = %d, "
					"maxTickIndexToSend = %d",
				gameTime,
				gameTime - reader.firstGameTime,
				maxTickIndexToSend )

			raise DelayException


	def start( self ):
		"""
		This method starts the producer, beginning writing out of file data.
		"""
		self.request.registerProducer( self, True )
		self.isPaused = False


	def write( self ):
		"""
		This method writes an amount of data to the client.
		"""
		if self.isPaused:
			return

		if not self.request:
			return

		now = time.time()

		pauseDuration = self.lastPauseDuration
		self.lastPauseDuration = 0.0

		lastWriteTime = self.lastWriteTime
		self.lastWriteTime = now

		timeWaitingForRead = None

		if self.lastReadTime is not None:
			# We might have been paused due to stalling from the client-side,
			# so discount that time when determining time since last read for
			# the purposes of WAIT_READ_TIMEOUT.
			#  lRT .... lWT............... now
			timeWaitingForRead = now - pauseDuration - self.lastReadTime

		data = self.fileReader.read( self.offset, Config.SEND_BUFFER_SIZE )

		log.debug( "FileProducer.write( %s ): %s:%d: Read %d from offset = %d",
			self.fileReader.path,
			self.request.client.host, self.request.client.port,
			len( data ) if data is not None else 0,
			self.offset )


		MODE_WRITE_BITS = 0222
		isFileWritable = ((self.fileReader.stat.st_mode & MODE_WRITE_BITS) != 0)

		if data is None:
			if (self.offset == self.fileReader.stat.st_size) and \
					not isFileWritable:
				log.info( "FileProducer.write( %s ): "
						"Finished sending to client %s:%d (send buffer %d bytes)",
					self.fileReader.path,
					self.request.client.host, self.request.client.port,
					len( self.sendBuffer ) )

				self.request.write( self.sendBuffer )
				self.sendBuffer = ''
				self.disconnect()
			else:
				if timeWaitingForRead is not None and \
						(timeWaitingForRead >= Config.WAIT_READ_TIMEOUT):

					log.debug( "FileProducer.write( %s ): %s:%d: "
							"offset = %d, size = %d, mode = %o",
						self.fileReader.path,
						self.request.client.host, self.request.client.port,
						self.offset, self.fileReader.stat.st_size,
						self.fileReader.stat.st_mode )

					log.error( "FileProducer.write( %s ): "
							"Disconnecting client %s:%d due to no new data "
							"read after %.01fs (%s read-writeable)",
						self.fileReader.path,
						self.request.client.host, self.request.client.port,
						timeWaitingForRead,
						"is" if isFileWritable else "not" )

					self.disconnect()
			return

		self.lastReadTime = now

		lastReadPosition = self.replayFileReader.numBytesRead

		log.debug( "FileProducer.write( %s ): "
				"Got %d bytes of data from offset = %d. "
				"Reader read = %d, added = %d",
			self.fileReader.path,
			len( data ),
			self.offset,
			self.replayFileReader.numBytesRead,
			self.replayFileReader.numBytesAdded )

		try:
			if random.random() < \
					Config.ARTIFICIAL_BAD_DATA_READ_PROBABILITY:
				# For debugging
				raise AddDataException( "Artificial bad data read" )

			try:
				self.replayFileReader.addData( data )
			except ValueError as e:
				# Convert to AddDataException
				raise AddDataException( str( e ) )

		except DelayException as e:

			offset = self.replayFileReader.numBytesRead

			log.debug( "FileProducer.write( %s ): "
					"Delay constrains sending up to offset %d "
					"(%d of %d read bytes)",
				self.fileReader.path,
				offset,
				offset - self.offset,
				len( data ) )

			self.replayFileReader.clearError()

			# Reduce the data to add only to position indicated by the
			# numBytesRead. This should be the end of the last chunk
			# that is allowed to be streamed as constrained by the time-delay.

			if offset <= self.offset:
				# Tick data was originally in buffered data.
				return

			data = data[:offset - self.offset]
			# Disable delay detection temporarily.
			self.replayFileReader.listener = None
			self.replayFileReader.addData( data )
			self.replayFileReader.listener = self

		except AddDataException as e:
			log.debug( "FileProducer.write( %s ): Reader reported bad data at "
					"numBytesRead = %d, numBytesAdded = %d, offset = %d: %s",
				self.fileReader.path,
				self.replayFileReader.numBytesRead,
				self.replayFileReader.numBytesAdded,
				self.offset,
				e )

			# Rewind the offset back to the last known good position, discarding
			# any buffered data which has now been found to contain bad data.
			self.sendBuffer = ''
			self.replayFileReader.clearBuffer()
			self.fileReader.scrub( self.replayFileReader.numBytesRead )
			self.offset = self.replayFileReader.numBytesRead

			timeWaitingForGoodRead = None
			if self.lastGoodReadTime is not None:
				timeWaitingForGoodRead = now - pauseDuration - \
					self.lastGoodReadTime

			if timeWaitingForGoodRead is not None and \
					(timeWaitingForGoodRead >= Config.WAIT_READ_TIMEOUT):
				log.error( "FileProducer.write( %s ): "
						"Disconnecting client %s:%d due to persistent bad "
						"data reading after %.01fs",
					self.fileReader.path,
					self.request.client.host, self.request.client.port,
					timeWaitingForGoodRead )
				self.disconnect()
			else:
				self.replayFileReader.clearError()
			return

		log.debug( "FileProducer.write( %s ): "
				"Added %d bytes of data from offset = %d. "
				"Reader read = %d, added = %d",
			self.fileReader.path,
			len( data ),
			self.offset,
			self.replayFileReader.numBytesRead,
			self.replayFileReader.numBytesAdded )

		self.lastGoodReadTime = now
		previousOffset = self.offset
		self.offset = self.replayFileReader.numBytesAdded

		# Check how much the reader has advanced, if any. Buffer any data that
		# has been added but not verified yet so we can send it later.
		if lastReadPosition == self.replayFileReader.numBytesRead:
			self.sendBuffer += data

			log.debug( "FileProducer.write( %s ): "
					"Buffered %d from offset %d, read pos %d",
				self.fileReader.path,
				len( data ),
				self.offset - len( data ),
				self.replayFileReader.numBytesRead )

			return

		# The reader has advanced, so we can send our data now up to where
		# it has advanced to, buffering the rest.
		dataToSend = self.sendBuffer + \
			data[:self.replayFileReader.numBytesRead - previousOffset]
		self.sendBuffer = \
			data[self.replayFileReader.numBytesRead - previousOffset:]

		self.request.write( dataToSend )
		HTTPReplayService.bytesSent += len( data )

		log.debug( "FileProducer.write( %s ): Reader advanced from %d to %d, "
				"wrote %d bytes, buffered %d",
			self.fileReader.path,
			lastReadPosition,
			self.replayFileReader.numBytesRead,
			len( dataToSend ),
			len( self.sendBuffer ) )


	def disconnect( self ):
		"""
		This method is called to finish sending data to the client.
		"""
		log.info( "FileProducer.disconnect( %s ): Client %s:%d",
			self.fileReader.path,
			self.request.client.host, self.request.client.port )

		self.request.unregisterProducer()
		self.request.finish()
		self.stopProducing()


	def pauseProducing( self ):
		"""
		Override from IPushProducer.
		"""
		_replaySender.removeClient( self )
		self.isPaused = True
		self.pauseStartTime = time.time()
		log.debug( "FileProducer.pauseProducing( %s ): Client %s:%d",
			self.fileReader.path,
			self.request.client.host, self.request.client.port )


	def resumeProducing( self ):
		"""
		Override from IPushProducer.
		"""
		_replaySender.addClient( self )
		self.isPaused = False
		self.lastPauseDuration += (time.time() - self.pauseStartTime)
		self.pauseStartTime = None

		log.debug( "FileProducer.resumeProducing( %s ): Client %s:%d "
				"(paused %.01fs)",
			self.fileReader.path,
			self.request.client.host, self.request.client.port,
			self.lastPauseDuration )

		self.write()


	def stopProducing( self ):
		"""
		Override from IPushProducer.
		"""
		log.debug( "FileProducer.stopProducing( %s ): Client %s:%d",
			self.fileReader.path, 
			self.request.client.host, self.request.client.port )

		_replaySender.removeClient( self )
		self.request = None
		self.fileReader.numClients -= 1



class ReplayFileDescriptor( object ):
	"""
	This class represents a descriptor for a replay file.
	"""
	def __init__( self, path, stat, header, metaData ):
		"""
		Constructor.

		@param path 	The file resource path.
		@param stat 	The stat() of the file.
		@param header 	The replay header.
		@param metaData The replay meta-data.
		"""
		self._path = path
		self._stat = stat
		self._header = header
		self._metaData = metaData


	@property
	def path( self ):
		"""
		This attribute is the resource path of the replay file.
		"""
		return self._path

	@property
	def stat( self ):
		"""
		This attribute is the results of stat() on the replay file.
		"""
		return self._stat

	@property
	def header( self ):
		"""
		This attribute is the header of the replay file, as a dict.
		"""
		return self._header

	@property 
	def metaData( self ):
		"""
		This attribute is the meta-data of the replay file.
		"""
		return self._metaData

	def __str__( self ):
		return '<ReplayFileDescriptor: %s>' % self._path


class ReplayFileInfoDescriptorEncoder( json.JSONEncoder ):
	"""
	This class extends JSONEncoder to encode ReplayFileDescriptor.
	"""
	def __init__( self, documentRoot, *args, **kwargs ):
		"""
		Constructor.

		@param documentRoot 	The top-level recordings directory.
		"""
		json.JSONEncoder.__init__( self, *args, **kwargs )
		self._documentRoot = documentRoot


	def default( self, obj ):
		"""
		Override from JSONEncoder.
		"""
		if isinstance( obj, ReplayFileDescriptor ):
			path = obj.path
			if path.startswith( self._documentRoot ):
				path = obj.path[len( self._documentRoot ):]
				if path.startswith( '/' ):
					path = path[1:]

			return dict( path = path, 
				size = obj.stat.st_size,
				mtime = obj.stat.st_mtime,
				header = obj.header, 
				metaData = obj.metaData )

		return json.JSONEncoder.default( self, obj )


class ReplayHeaderReader( object ):
	"""
	This class reads a replay file until the header and meta-data have been
	read.
	"""
	def __init__( self, path ):
		"""
		Constructor.

		@param path 	The replay file resource path.
		"""
		self._path = path
		self._stat = None
		self._header = None 
		self._metaData = None


	def getDescriptor( self, previousDescriptor = None ):
		"""
		This method returns the descriptor for this file by reading the header
		and meta-data.

		@param  previousDescriptor 	A copy of the previous descriptor. If the
									modification time is the same, this is
									returned straight-away.

		@return a descriptor for the replay file.
		"""
		reader = BigWorld.ReplayDataFileReader()
		reader.listener = self

		absPath = ResMgr.resolveToAbsolutePath( self._path )
		self._stat = os.stat( absPath )
		if previousDescriptor and \
				(self._stat.st_mtime == previousDescriptor.stat.st_mtime):
			return previousDescriptor

		with open( self._path, "rb" ) as f:
			isDone = False 
			while not isDone:
				block = f.read( Config.REPLAY_FILE_CACHE_READ_BLOCK_SIZE )
				if not block:
					isDone = True
				else:
					reader.addData( block )
					if self._header is not None and self._metaData is not None:
						isDone = True

			if self._header is None or self._metaData is None:
				raise ValueError( "Invalid replay file" )

			return ReplayFileDescriptor( self._path, self._stat, self._header, 
				self._metaData )


	def onReplayDataFileReaderHeader( self, reader, header ):
		"""
		This method is callback from the replay file reader when the header has
		been read.

		@param reader 	The reader instance.
		@param header 	The header.
		"""

		# Convert it to a dictionary for JSON encoding.
		self._header = dict( version = header.version, 
			digest = header.digest,
			numTicks = header.numTicks,
			timestamp = header.timestamp )


	def onReplayDataFileReaderMetaData( self, reader, metaData ):
		"""
		This method is a callback from the replay file reader when the
		meta-data block has been read.

		@param reader 	The reader instance.
		@param metaData	The meta-data as a dictionary of key-value pairs.
		"""
		self._metaData = metaData


def resmgrwalk( path, *args, **kwargs ):
	"""
	Wrapper for os.walk() to use resource paths.
	"""
	absolutePath = ResMgr.resolveToAbsolutePath( path )
	absolutePathLocation = absolutePath[:-len( path )]

	for path, dirList, fileList in os.walk( absolutePath, *args, **kwargs ):
		# Transform path to resource path
		path = path[len( absolutePathLocation ):]
		yield path, dirList, fileList


class IsFileCheckTask( BackgroundTask.BackgroundTask ):
	"""
	This class checks for a file's existence in the background,
	calling back on a deferred in the main thread.
	"""
	def __init__( self, path, deferred ):
		self._path = path
		self._deferred = deferred
		self._result = None

	def doBackgroundTask( self, mgr, threadData ):
		self._result = ResMgr.isFile( self._path )
		mgr.addMainThreadTask( self )

	def doMainThreadTask( self, mgr ):
		self._deferred.callback( self._result )



class ReplayFileCacheRefreshTask( BackgroundTask.BackgroundTask ):
	"""
	This class is a task for traversing the recordings directory and reading
	file data in the background.
	"""
	def __init__( self, cache, documentRoot, originalDescriptors ):
		"""
		Constructor.

		@param cache 			The replay file cache to refresh.
		@param documentRoot 	The top-level recordings directory.
		@param originalDescriptors
								The results from a previous refresh. Files that
								haven't been modified since the previous
								refresh will be assumed to have stayed the
								same.
		"""
		self._descriptors = {}
		self._cache = cache
		self._documentRoot = documentRoot
		self._originalDescriptors = originalDescriptors
		self._failure = None

	def doBackgroundTask( self, mgr, threadData ):
		"""
		Override from BackgroundTask.
		"""
		try:
			for path, dirList, fileList in resmgrwalk( self._documentRoot ):
				for fileName in fileList:
					if not Config.REPLAY_FILE_PATTERN.match( fileName ) or \
							Config.REPLAY_FILE_NON_PATTERN.match( fileName ):
						continue

					filePath = os.path.join( path, fileName )
					
					try:
						reader = ReplayHeaderReader( filePath )
						descriptor = reader.getDescriptor( 
							self._originalDescriptors.get( filePath, None ) )
						self._descriptors[descriptor.path] = descriptor
					except ValueError as e:
						# Skip this file, not a valid replay file.
						continue
		except:
			self._failure = Failure()

		mgr.addMainThreadTask( self )


	def doMainThreadTask( self, mgr ):
		"""
		Override from BackgroundTask.
		"""
		if self._failure is not None:
			self._cache.onRefreshTaskFailed( self, self._failure )
			return

		self._cache.onRefreshTaskComplete( self, self._descriptors )


class ReplayFileCache( object ):
	"""
	This class holds cached replay file descriptors.
	"""
	def __init__( self, taskMgr, documentRoot ):
		"""
		Constructor.

		@param taskMgr 			A background task manager instance.
		@param documentRoot 	The top-level recordings directory.
		"""
		self._documentRoot = documentRoot

		self._files = {}

		self._taskMgr = taskMgr 
		self._task = None
		self._deferred = None
		self._lastRefreshTime = None


	@property
	def files( self ):
		"""
		This attribute returns an iterator through the cached file descriptors.
		"""
		return iter( self._files.values() )


	def startRefresh( self ):
		"""
		Request to refresh the cache. Returns a deferred which can be be used
		to register a callback when complete. 

		May not actually refresh the cache if too soon since the last refresh.
		"""
		if self._task is None:
			if self._lastRefreshTime is not None and \
					(time.time() - self._lastRefreshTime) < \
						Config.REPLAY_FILE_CACHE_REFRESH_MIN_TIME:
				# Return the old ones
				return defer.succeed( self.files )

			self._deferred = defer.Deferred()
			self._task = ReplayFileCacheRefreshTask( self, self._documentRoot, 
				self._files )
			self._taskMgr.addBackgroundTask( self._task )

		return self._deferred


	def onRefreshTaskComplete( self, task, descriptors ):
		"""
		Called when the background refresh task completes successfully.

		@param task 		The task that failed.
		@param descriptors 	The new descriptors.
		"""
		if task is self._task and self._deferred:
			self._files = descriptors
			self._lastRefreshTime = time.time()
			deferred = self._deferred
			self._deferred = None
			deferred.callback( self.files )
			self._task = None


	def onRefreshTaskFailed( self, task, failure ):
		"""
		Called when the background refresh task fails.

		@param task 	The task that failed.
		@param failure	The failure.
		"""
		if task is self._task and self._deferred:
			deferred = self._deferred
			self._deferred = None
			self._task = None
			self._files = []
			deferred.errback( failure )


	def stop( self ):
		"""
		Called to cancel a pending task.
		"""
		self._task = None
		self._deferred = None


class ReplayResource( Resource ):
	"""
	This class implements a resource for streaming a replay file.
	"""


	def __init__( self, path, bgTaskMgr ):
		"""
		Constructor.

		@param path 		The path to the file to serve.
		"""
		Resource.__init__( self )
		self._path = path
		self._bgTaskMgr = bgTaskMgr


	def render_GET( self, request ):
		"""
		Override from Resource.
		"""

		deferred = defer.Deferred()

		def callback( isFileResult ):
			if not isFileResult:
				request.render( _childNotFound )
				return

			request.setHeader( "Content-Type", "application/octet-stream" )
			offset = request.getHeader( "Range" )
			# TODO: Make this handle all Range: header formats
			# There is twistedweb.static.File._parseRangeHeader
			if offset == None:
				offset = 0
			else:
				offset = int(offset[0:offset.find("-")])

			request.setHeader( "Content-Range", "bytes */*" )
			reader = _replaySender.openPath( self._path )
			producer = Config.FILE_PRODUCER_FACTORY( request, reader, offset )
			producer.start()
			_replaySender.addClient( producer )

		deferred.addCallback( callback )
		task = IsFileCheckTask( self._path, deferred )
		self._bgTaskMgr.addBackgroundTask( task )

		return NOT_DONE_YET


class ReplayJSONListResource( Resource ):
	def __init__( self, bgTaskMgr, cache, documentRoot ):
		"""
		Constructor.

		@param cache 		The ReplayFileCache.
		@param documentRoot The replay file document root.
		"""
		Resource.__init__( self )

		self._bgTaskMgr = bgTaskMgr
		self._cache = cache
		self._documentRoot = documentRoot


	def getChild( self, path, request ):
		"""
		Override from Resource.
		"""

		if not path:
			return self

		filePath = os.path.join( self._documentRoot, path )

		return ReplayResource( filePath, self._bgTaskMgr )


	def render_GET( self, request ):
		"""
		Override from Resource.
		"""
		deferred = self._cache.startRefresh()

		requestedVersion = request.args.get( 'version', [None] )[0]
		requestedDigest = request.args.get( 'digest', [None] )[0]
		requestedAllMetaData = request.args.get( 'meta_data_match', [] )
		requestedAnyMetaData = request.args.get( 'meta_data_any', [] )

		def metaDataMatch( descriptor ):
			for match in requestedAllMetaData:
				try:
					key, value = match.split( ':' )
					if descriptor.metaData.get( key ) != value:
						return False
				except:
					# Return nothing for bad queries  
					return False


			if requestedAnyMetaData:
				for match in requestedAnyMetaData:
					try:
						key, value = match.split( ':' )
						if descriptor.metaData.get( key ) == value:
							return True
					except:
						# Return nothing for bad queries
						return False
				return False

			return True
				


		def callback( files ):
			request.setHeader( "Content-Type", "application/json" )

			filteredFiles = [f for f in files 
				if (requestedVersion is None or 
					(f.header['version'] == requestedVersion)) and
				(requestedDigest is None or
					(f.header['digest'] == requestedDigest)) and
				metaDataMatch( f ) ]

			encoder = ReplayFileInfoDescriptorEncoder( self._documentRoot,
				separators = (',', ':') )

			for chunk in encoder.iterencode( filteredFiles ):
				request.write( chunk )

			request.finish()
				
		def errback( failure ):
			log.error( "ReplayJSONListResource.render_GET: "
					"Failed cache refresh: %s",
				failure )

			request.write( "Server error" )
			request.finish()


		deferred.addCallbacks( callback, errback )

		return NOT_DONE_YET



class ReplayHTMLIndexResource( Resource ):
	"""
	This class implements a resource for rendering an index view of the replay
	directory.
	"""

	def __init__( self, cache, documentRoot ):
		"""
		Constructor.

		@param documentRoot 	The directory to serve recordings from.
		"""

		self._cache = cache
		self._documentRoot = documentRoot

		Resource.__init__( self )


	def getChild( self, path, request ):
		"""
		Override from Resource.
		"""

		if not path:
			return self

		return _childNotFound


	def render_GET( self, request ):
		"""
		Override from Resource.
		"""

		deferred = self._cache.startRefresh()

		def callback( files ):
			files = list( files )

			request.setHeader( "Content-Type", "text/html" )

			request.write( "<html><body><h1>Index of %s</h1><ul>" % 
				self._documentRoot )

			for fileDescriptor in files:
				path = fileDescriptor.path
				if path.startswith( self._documentRoot ):
					path = path[len( self._documentRoot ):]
					if path.startswith( "/" ):
						path = path[1:]

				hrefPath = "/replays/" + path
				request.write( 
					"<li><a href=\"%s\">%s</a> (%s, %d bytes)</li>" %
						(hrefPath, path, 
							"live" if fileDescriptor.header['numTicks'] == 0 
								else "complete", 
							fileDescriptor.stat.st_size) )
			request.write( "</ul></body></html>" )

			request.finish()
				
		def errback( failure ):
			log.error( "ReplayHTMLListResource.render_GET: "
					"Failed cache refresh: %s",
				failure )

			request.write( "Server error" )
			request.finish()

		deferred.addCallbacks( callback, errback )

		return NOT_DONE_YET


class TopLevelResource( Resource ):
	"""
	The top-level resource.
	"""

	def __init__( self, bgTaskMgr, replayFileCache, documentRoot ):
		"""
		Constructor.

		@param replayFileCache 	The replay file cache.
		@param documentRoot 	The top-level recordings directory.
		"""
		Resource.__init__( self )

		self._bgTaskMgr = bgTaskMgr
		self._documentRoot = documentRoot
		self._htmlIndex = ReplayHTMLIndexResource( replayFileCache,
			documentRoot )
		self._jsonList = ReplayJSONListResource( bgTaskMgr, replayFileCache,
			documentRoot )


	def getChild( self, path, request ):
		""" Override from Resource. """
		if path == "html":
			return self._htmlIndex
		elif path == "replays":
			return self._jsonList
		elif path:
			filePath = os.path.join( self._documentRoot, path )
			if not Config.SHOULD_MATCH_FILENAMES_AT_TOP_LEVEL:
				return _childNotFound

			return ReplayResource( filePath, self._bgTaskMgr )

		return self


	def render_GET( self, request ):
		""" Override from Resource. """

		# If you're coming from a browser, redirect to the HTML list resource.
		return redirectTo( "/html", request )



class HTTPReplayService( TwistedWeb ):
	"""
	Generic HTTP L{Bigworld.Service} for serving files from the 'res' tree
	subject to simple pattern-based whitelisting.

	See also L{ResTreeResource}.
	"""

	bytesSent = 0

	def __init__( self ):
		"""
		Constructor.
		"""
		self._bgTaskMgr = BackgroundTask.Manager()
		self._bgTaskMgr.startThreads( 1 )
		self._replayFileCache = ReplayFileCache( self._bgTaskMgr, 
			Config.DOCUMENT_ROOT )
		self._topLevelResource = TopLevelResource( self._bgTaskMgr,
			self._replayFileCache,
			Config.DOCUMENT_ROOT )
		TwistedWeb.__init__( self, portOrPorts = Config.PORTS,
			netmask = Config.NETMASK )

	def createResources( self ):
		""" Implements superclass method TwistedWeb.createResources """

		reactor.callWhenRunning(
			lambda: _replaySender.setup( self._bgTaskMgr ) )

		return self._topLevelResource


	def initWatchers( self, interface ):
		""" Overrides superclass method TwistedWeb.initWatchers """

		TwistedWeb.initWatchers( self, interface )

		BigWorld.addWatcher(
			"services/HTTPReplayService/bytesSent",
			lambda: "%d" % ( HTTPReplayService.bytesSent ) )
		BigWorld.addWatcher(
			"services/HTTPReplayService/clientsInQueue",
			lambda: "%d" % ( len(_replaySender.clients) ) )
		BigWorld.addWatcher(
			"services/HTTPReplayService/activeFiles",
			lambda: "%d" % ( len(_replaySender.activeFiles) ) )
		BigWorld.addWatcher(
			"services/HTTPReplayService/isTaskRunning",
			lambda: "true" if _replaySender.isTaskRunning else "false" )

	def finiWatchers( self ):
		""" Override from TwistedWeb. """

		BigWorld.delWatcher( "services/HTTPReplayService/bytesSent" )
		BigWorld.delWatcher( "services/HTTPReplayService/clientsInQueue" )
		BigWorld.delWatcher( "services/HTTPReplayService/activeFiles" )
		BigWorld.delWatcher( "services/HTTPReplayService/isTaskRunning" )

		TwistedWeb.finiWatchers( self )


	def onDestroy( self ):
		self._replayFileCache.stop()
		_replaySender.tearDown()
		self._bgTaskMgr.stopAll()


# HTTPReplayService.py
