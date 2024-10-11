
import BigWorld
import logging

log = logging.getLogger( __name__ )


class EntityRecorder( object ):
	"""
	Performs simple timer-based collection of arbitrary game data, typically for
	the purposes of game analytics.

	Example usage:

		class MyEntity( Avatar ):

			recorder = EntityRecorder(
				"entity_positions",
				["entity id", "entity type", "x", "z"]
			)

			def onMatchBegin( self ):
				self.recorder.startRecording( self.recordEntityPositions )
				...

			def onMatchEnd( self ):
				self.recorder.stopRecording()
				...

			def recordEntityPositions( self, *ignore ):
				for e in BigWorld.entities.values():
					self.recorder.record(
						e.id, e.className, e.position[0], e.position[2] )

	See also BigWorld document "How to Game Analytics".
	"""

	# serialises a sequence of fields into a CSV-format line
	formatCSV = lambda fields: ','.join( '"' + str( f ) + '"' for f in fields ) + '\n'


	def __init__( self, name, fieldList,
		snapshotFrequency = 2, formatter = formatCSV ):
		"""

		@param name
		Canonical name for this recorder; will be used as output filename.

		@param fieldList
		List of data fields this recorder will write; used to write file header.

		@param snapshotFrequency
		Time interval between snapshots in seconds.

		@param formatter
		A callable that formats a list of fields into a formatted
		line. Default is to format fields as CSV.
		"""

		self.name = name
		self.snapshotFrequency = snapshotFrequency
		self.fields = fieldList
		self.formatter = formatter

		# bigworld timer id
		self.timerId = None

		# name of output file
		self.outputFilename = self.name + '.csv'

		# output file-like object we will write to
		self.outputStream = None

	# __init__


	def record( self, *args ):
		""" Record a tick of data. Default implementation raises
		L{NotImplementedError}. """
		raise NotImplementedError()
	# record


	def startRecording( self, recordCallback = None ):
		""" Starts or restarts a recording. A callable recording method
		can be optionally given that will be called periodically with a BigWorld
		timer ID as argument. It is expected to call writeData one or more times
		as required. """

		if self.timerId:
			log.warning( "Recorder '%s' already recording", self.name )
			return

		if not self.outputStream:
			try:
				self.outputStream = open( self.outputFilename, 'w' )
			except IOError, ex:
				log.warning(
					"Couldn't open file '%s' for writing", self.outputFilename )
				raise

		headerLine = self.formatter( self.fields )
		self.outputStream.write( headerLine )

		self.timerId = BigWorld.addTimer(
			recordCallback or self.record, 0, self.snapshotFrequency )

		log.info(
			"%s: started recording, timer id = %d" %
			(self.__class__.__name__, self.timerId) )
	# startRecording


	def stopRecording( self ):
		""" Stops a recording. """

		if not self.timerId:
			log.warning( "Recorder '%s' not recording", self.name )
			return

		BigWorld.delTimer( self.timerId )
		self.timerID = None
		try:
			self.outputStream.close()
		except:
			pass
		self.outputStream = None

		log.info( "%s: stopped recording", self.__class__.__name__ )
	# stopRecording


	def writeData( self, *fields ):
		""" Write given fields to this recorder's output stream. Default
		implementation writes values in CSV format. """

		if not self.outputStream:
			raise Exception( "Can't write data until recording started" )

		if not fields:
			raise ValueError( "No fields passed" )

		line = self.formatter( fields )
		self.outputStream.write( line )
	# writeData

# end class EntityRecorder


class EntityPositionRecorder( EntityRecorder ):
	"""
	Example sub-class of L{EntityRecorder} for recording the positions
	of specfic entity types for a specific space.

	Example usage:

		from EntityRecorder import EntityRecorder, EntityPositionRecorder

		r = EntityPositionRecorder( "highlands", 2 )
		r.startRecording()

		...

		r.stopRecording()

	"""

	def __init__( self, name, spaceId, entityTypes = None ):
		EntityRecorder.__init__( self, name,
			["entity id", "entity type", "x", "z"] )

		self.spaceId = spaceId
		self.entityTypes = entityTypes
	# __init__


	def record( self, *args):
		numWritten = 0
		for e in BigWorld.entities.values():
			if e.spaceID != self.spaceId:
				continue

			if self.entityTypes and (e.className not in self.entityTypes):
				continue

			numWritten += 1
			self.writeData( e.id, e.className, e.position[0], e.position[2] )

		# log.debug( "Recorded %d entities", numWritten )
	# record

# end class EntityPositionRecorder


class EntityEventRecorder( EntityRecorder ):
	"""
	Example sub-class of L{EntityRecorder} for recording events instead of
	properties. Introduces a new method L{recordEvent}, which buffers the passed
	event fields until the next write flushes the buffer.


	Example usage:

		from EntityRecorder import EntityRecorder, EntityPositionRecorder
		from time import time as now

		class Player( BigWorld.Entity ):

			r = EntityPositionRecorder(
				"my_events", ['timestamp', 'event name', 'x', 'z'] )

			def onMatchBegin( self ):
				r.startRecording()
				...

			def onMatchEnd( self ):
				r.stopRecording()
				...

			def onPlayerDeath( self ):
				(x ,y, z) = self.position
				r.recordEvent( now(), 'player death', x, z )
				...

	"""

	def __init__( self, *args, **kwargs ):
		EntityRecorder.__init__( self, *args, **kwargs )
		self.eventBuffer = []
	# __init__


	def record( self, *args ):

		for eventFieldList in self.eventBuffer:
			self.writeData( *eventFieldList )

		del self.eventBuffer[:]
		# log.debug( "Recorded %d events", numWritten )
	# record


	def recordEvent( self, *fields ):
		""" Records (buffers) the given fields to be flushed on the next
		call to L{record}. """
		self.eventBuffer.append( fields )
	# recordEvent

# end class EntityEventRecorder

# EntityRecorder.py

