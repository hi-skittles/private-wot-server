# entity getter

import string
import socket
import select
import sys
import os
import types
import time
from StringIO import StringIO

import bwsetup; bwsetup.addPath( ".." )
from pycommon.messages import *

class CellTalker:

	"""
	Handles TCP connection to a CellApp.exe
	"""

	# using chars here for easy debugging...
	GET_ENTITY_TYPE_NAMES ='n'
	GET_ENTITIES = 'b'
	GET_GRID = 'e'

	REAL = '0'
	GHOST = '1'

	def __init__( self, spaceId, cellOrAddr ):
		"""
		cellOrAddr should be a LeafNode object from the CellAppMgrTalker
		module when this process is a logger, and should be an IPv4 address
		tuple when this process is a viewer.  Note that the address is a
		network byte order (int, short) tuple, not the normal Python
		(string, short) address tuple.
		"""
		if not spaceId:
			raise TypeError("Invalid spaceId")

		self.entityData = []
		self.ghostEntityData = []
		
		#: (minX, minY, minZ, maxX, maxY, maxZ), which corresponds 
		#: with ( west, bottom, south, east, top, north ).
		self.spaceBounds = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
		self.gridData = {}
		self.typeName = {}
		self.spaceId = spaceId
		self.gridResolution = 100.0

		# We use this to regulate the freq of real, ghost updates
		self.stage = 0

		# A mapping from message keys to a tuple of:
		# - the buffer used to store the most recent message of that type
		# - the timestamp of the last time this stream was modified
		self.streamBufs = {}
		for key in self.UPDATE_METHODS.keys():
			self.streamBufs[ key ] = [StringIO(), 0]

		# A tuple indicates this is an 'offline' CellTalker on a viewer process
		if isinstance( cellOrAddr, types.TupleType ):
			self.addr = cellOrAddr
			self.s = None

		# A cell object indicates this is an 'online' CellTalker on a logger
		else:
			cell = cellOrAddr
			self.addr = cell.addr
			self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.s.connect(
				(socket.inet_ntoa( struct.pack( "I", self.addr[0] ) ),
				 cell.viewerPort) )

	def getNumTypeNames( self ):
		return self.numTypes

	def getTypeName( self, id ):
		if id in self.typeName:
			return self.typeName[id]
		else:
			return "Entity"

	def getInetAddress( self ):
		""" Get ip address:port as string. """
		if not self.addr:
			return None
			
		return "%s:%s" % ( socket.inet_ntoa( struct.pack( "I", self.addr[0] ) )
						, self.addr[1] )
		

	def getGrid( self ):
		"""
		Get the grid from the server
		"""

		# TODO: This is no longer used. The loaded grid information is now
		# received from the CellAppMgr. We should remove this code.
		key = self.GET_GRID

		# Send request if we're online
		if self.s:
			self._request( struct.pack( "<cI", self.GET_GRID, self.spaceId ),
						   key )

		# Terminating zero (strictly speaking this is unnecessary, since we know
		# when the end of the tree has come from the DFS algo)
		data = self._getNBytes( 4, key )
		isOkay, = struct.unpack( "<i", data )
		if not isOkay:
			raise socket.error(
				"This CellApp (%s) does not appear to be handing requested "
				"spaceId %s" % ( self.getInetAddress(), self.spaceId ) )

		self.spaceBounds = struct.unpack("<ffffff",
										 self._getNBytes( 4*3*2, key ) )
		self.gridResolution, = struct.unpack( "<f", self._getNBytes( 4, key ) )
		self.gridData = self._retrieveChunks()

	def getReals( self ):

		key = (self.GET_ENTITIES, self.REAL)

		# Send request if online
		if self.s:
			self._request( struct.pack("<ccI", self.GET_ENTITIES, self.REAL,
									   self.spaceId ), key )

		self.entityData = self._retrieveEntities( self.REAL )

	def getGhosts( self ):

		key = (self.GET_ENTITIES, self.GHOST)

		# Send request if online
		if self.s:
			self._request( struct.pack("<ccI", self.GET_ENTITIES, self.GHOST,
									   self.spaceId ), key )

		self.ghostEntityData = self._retrieveEntities( self.GHOST )

	def getTypeNames( self ):
		"""
		Retrieve a list of type names from the cellapp.
		"""

		# Clear the previous typename before setting them
		self.numTypes = 0
		self.typeName = {}

		key = self.GET_ENTITY_TYPE_NAMES

		# Send request if online
		if self.s:
			self._request( struct.pack( "<c", self.GET_ENTITY_TYPE_NAMES ),
						   key )

		# Parse types
		self.numTypes, = struct.unpack( "<I", self._getNBytes( 4, key ) )
		for i in range(self.numTypes):
			nameSize, = struct.unpack( "<H", self._getNBytes( 2, key ) )
			self.typeName[i] = self._getNBytes( nameSize, key )

	def update( self ):

		# We get reals every tick
		self.getReals()

		# We get ghosts once every 3 ticks
		if self.stage == 0:
			self.getGhosts()
		self.stage = (self.stage + 1) % 3

		if self.typeName == {}:
			self.getTypeNames()

		if self.spaceBounds == [0.0]*6:
			self.getGrid()

	# A map from streamBuf keys to the methods used to update those keys
	UPDATE_METHODS = { GET_ENTITY_TYPE_NAMES: getTypeNames,
					   GET_GRID: getGrid,
					   (GET_ENTITIES, REAL): getReals,
					   (GET_ENTITIES, GHOST): getGhosts	}

	# --------------------------------------------------------------------------
	# Section: Private Methods
	# --------------------------------------------------------------------------

	def _getNBytes( self, n, key ):
		"""
		OK, this is the hacky bit.  If we're online (talking to a cellappmgr)
		then this reads from the socket and records everything it reads into the
		streamBuf for the given key.

		If we're offline, this reads from the streamBuf for the given key.

		A key can be anything unique - for GET_ENTITY_TYPE_NAMES and GET_GRID it
		is just the message id, since they have no other parameters (other than
		the space), but for GET_ENTITIES it is either (GET_ENTITIES, REAL) or
		(GET_ENTITIES, GHOST) since we must cache both streams.
		"""

		# Online read function
		if self.s:
			def fetch( n ):
				data = self.s.recv( n )
				self.streamBufs[ key ][0].write( data )
				self.streamBufs[ key ][1] = time.time()
				return data

		# Offline read function
		else:
			def fetch( n ):
				return self.streamBufs[ key ][0].read( n )

		toGet = n;
		toRet = '';
		while toGet > 0:
			incoming = fetch( toGet )

			if len( incoming ) == 0:
				return toRet

			toRet += incoming;
			toGet -= len( incoming )

		return toRet

	def _request( self, msg, key ):

		# Send request
		if not self.s.send( msg ):
			raise RuntimeError, "socket connection broken"

		# Extract message ID
		id = msg[0]

		# Clear streamBuf
		buf = self.streamBufs[ key ][0]
		buf.seek( 0 )
		buf.truncate()

	def _retrieveChunks( self ):
		# TODO: This grid data is no longer used. Now uses the data sent by the
		# CellAppMgr. We may want to look at this at some stage esp. if people
		# start using multiple ChunkDirMappings.
		gridData = {}

		key = self.GET_GRID

		incoming = self._getNBytes( 4, key )
		num = struct.unpack("<I", incoming)[0]

		for num in range(num):
			incoming = self._getNBytes( 4*3, key )
			incomingUnpacked = struct.unpack( "<iii", incoming );
			y = incomingUnpacked[0]
			x1 = incomingUnpacked[1]
			x2 = incomingUnpacked[2]
			gridData[y] = (x1,x2)

		return gridData

	def _retrieveEntities( self, entityType ):

		entityData = []

		# The streamBuf key for fetching this type of entity
		key = (self.GET_ENTITIES, entityType)

		# get number of cells in space
		incoming = self._getNBytes( 4, key )

		try:
			(num,) = struct.unpack( "<i", incoming )
		except struct.error:
			print "ERROR: Not enough bytes on stream to unpack number of cells!"
			raise socket.error
		if num == -1:
			raise socket.error
		for i in range(num):
			incoming = self._getNBytes( 14, key )
			# x, y, typeid, id
			incomingUnpacked = struct.unpack( "<ffHI", incoming );
			entityData += [(incomingUnpacked[0],incomingUnpacked[1],incomingUnpacked[2],incomingUnpacked[3])]
		tmpEntityData = [(-x[3],x) for x in entityData]
		tmpEntityData.sort()
		entityData = [x for (key,x) in tmpEntityData]

		return entityData

# cell_talker.py
