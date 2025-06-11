import socket
import struct
import select
import copy
import StringIO

import bwsetup; bwsetup.addPath( ".." )
from pycommon.util import MFRectangle
from pycommon.watcher_data_type import BW_UNPACK3 as BW_UNPACK3

class BranchNode( object ):
	"""
	Encapsulates a server space partition in a binary space partition (BSP) 
	tree. 
	"""

	def __init__( self, position, load, aggression, isHorizontal ):

		#: whether partition is oriented horizontally (parallel to x-axis)
		self.isHorizontal = isHorizontal

		#: position of partition
		self.position = position

		#: sum of avg load of children
		self.load = load

		#: left child node
		self.left = None

		#: right child node
		self.right = None

		#: how aggressively this partition is being rebalanced (moving), 0-1.0
		self.aggression = aggression
	# __init__


	def __json__( self ):
		return self.__dict__
	# __json__


	def visit( self, rect, visitor ):
		leftRect = copy.deepcopy( rect )
		rightRect = copy.deepcopy( rect )

		if self.isHorizontal:
			leftRect.maxY = self.position
			rightRect.minY = self.position
			pt1 = (rect.minX, self.position)
			pt2 = (rect.maxX, self.position)
		else:
			leftRect.maxX = self.position
			rightRect.minX = self.position
			pt1 = (self.position, rect.minY)
			pt2 = (self.position, rect.maxY)

		if hasattr( visitor, "visitInterval" ):
			visitor.visitInterval( self, pt1, pt2 )

		self.left.visit( leftRect, visitor )
		self.right.visit( rightRect, visitor )
	# visit


	def printTree( self, depth = 0 ):
		print "  " * depth, self.isHorizontal, self.position
		self.left.printTree( depth + 1 )
		self.right.printTree( depth + 1 )
	# printTree
	

	def cellAt( self, x, y ):
		if (not self.isHorizontal and (x < self.position)) or \
				(self.isHorizontal and (y < self.position)):
			return self.left.cellAt( x, y )
		else:
			return self.right.cellAt( x, y )
	# cellAt

# class BranchNode


class LeafNode( object ):

	def __init__( self, addr, load, id, viewerPort, entityBoundLevels,
			chunkBounds, isRetiring, isOverloaded ):
		#: 	smoothed cpu load, 0.0-1.0
		self.load = load

		#: ip addr of CellApp
		self.addr = addr

		#: ip port of cellappmgr to talk to
		self.viewerPort = viewerPort

		#:	array of rectangles representing increments of cpu load 
		self.entityBoundLevels = entityBoundLevels

		#: rectangle around outdoor chunks, in world-space coords
		self.chunkBounds = chunkBounds

		#: 	unique CellApp id
		self.appID = id

		#:	flag indicating cellapp is about to disappear
		self.isRetiring = isRetiring

		#:	boolean flag indicating this cellapp has a dangerous load.
		self.isOverloaded = isOverloaded
		
	# __init__


	def __str__( self ):
		s = "LeafNode( appID: %d, " % self.appID
		s += "addr: %s, " % socket.inet_ntoa( struct.pack( "I", self.addr[0] )) 
		s += "port: %d, " % self.addr[1] 
		s += "load: %.2f, " % self.load
		s += "chunk bounds: %s, " % self.chunkBounds
		s += "entity bounds: %s )" % self.entityBoundLevels
		return s
	# __str__
	

	def __json__( self ):
		copy = dict( self.__dict__ )
		# copy['addr'] = self.getInetAddress()
		copy['addr'] = socket.inet_ntoa( struct.pack( "I", self.addr[0] ) )
		copy['port'] = copy['viewerPort']
		del copy['viewerPort']
		return copy
	# __json__
		

	def getInetAddress( self ):
		return "%s:%s" % ( socket.inet_ntoa( struct.pack( "I", self.addr[0] )) 
						, self.addr[1] ) 
	# getInetAddress


	def visit( self, rect, visitor ):
		if hasattr( visitor, "visitCell" ):
			visitor.visitCell( self, rect )
	# visit


	def printTree( self, depth = 0 ):
		print "  " * depth, hex( self.addr[0] ), hex( self.addr[1] )
	# printTree


	def cellAt( self, x, y ):
		return self
	# cellAt

# class LeafNode


class SocketFileWrapper:
	"""
	This class wraps a socket and makes it look a little like a file object.
	Well... only implements the read method for now.
	"""

	def __init__( self, socket ):
		self.socket = socket
	# __init__


	def read( self, numToRead ):
		numOutstanding = numToRead
		result = ''

		while numOutstanding > 0:
			incoming = self.socket.recv( numOutstanding );
			if len( incoming ) == 0:
				raise socket.error, "socket connection broken"

			result += incoming;
			numOutstanding -= len( incoming )

		return result
	# read

# SocketFileWrapper


class CellAppMgrTalker( object ):
	"""
	Handles TCP connection to the Cell App Manager.
	"""

	# These must match
	GET_CELLS = 'b'
	REMOVE_CELL = 'c'
	STOP_CELL_APP = 'd'
	GET_VERSION = 'e'
	GET_SPACE_GEOMETRY_MAPPINGS = 'f'

	def __init__( self, space, addr = None ):
		"""
		Create a talker for the given space, and optionally connect it to the
		cellappmgr at the given address.  Loggers will be connected, viewers
		will not.  This of course means that if a viewer calls any method that
		uses the socket, an exception will be thrown - naughty!
		"""

		self.appsTotal = 0
		self.space = space
		self.addr = addr

		# The following fields are only set for talker objects which are
		# actually connected to the cellappmgr (i.e. those running on loggers)
		if self.addr:

			# A buffer we use to record the network stream each tick
			self.streamBuf = StringIO.StringIO()

			# print "creating sock to %s:%s" % self.addr
			self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

			# as of current, requesting invalid data (eg: a space id for 
			# a space that doesn't exist) will block in the recv() call,
			# hence we set a timeout of half a sec rather than blocking
			# forever.
			self.s.settimeout( 0.5 )

			self.s.connect( self.addr )
			# print "connected"

			try:
				self.getCells()
			except socket.timeout, reason:
				print("getCells() timed out (perhaps space id=%s doesn't exist?)" 
					% space )
				raise
	# __init__


	def visit( self, rect, visitor ):
		if self.root:
			self.root.visit( rect, visitor )
	# visit

	def deleteCell( self, cell, sock = None ):

		# IP, port, salt, spaceID
		toSend = struct.pack( "<cIHHI", self.REMOVE_CELL,
				cell.addr[0], cell.addr[1], 0, cell.spaceId )

		# This is a bit wierd, but to save implementing this send() in two
		# places I've allowed specification of the socket to send the message on
		# so that a replayer can send this message to a logger, as well as the
		# normal case of the logger sending it to the actual cellappmgr.
		if sock == None:
			sock = self.s
		sock.send( toSend )


	def deleteCellApp( self, cell, sock = None ):
		# IP, port, salt
		toSend = struct.pack( "<cIHH", self.STOP_CELL_APP,
				cell.addr[0], cell.addr[1], 0 )

		# Same optional socket hackery as above
		if sock == None:
			sock = self.s
		sock.send( toSend )


	def cellAt( self, x, y ):
		return self.root.cellAt( x, y )


	def getCellAppID( self, addr ):
		if self.cells.has_key( addr ):
			return self.cells[ addr ].appID


	def getTitle( self ):
		return "Space %d. Cell Apps %d of %d" % \
			(self.space, len(self.cells), self.appsTotal)


	def getCells( self, streamBuf = None ):
		"""
		If streamBuf is None, this is a logger process fetching the BSP from a
		cellappmgr.  The stream read from the cellappmgr will be returned.

		If streamBuf is not None, this is a replayer process reconstructing the
		BSP from a stream sent by the logger.  Nothing is returned.
		"""

		if not streamBuf:
			fetch = lambda n: self._getNBytes( n )

			# Clear old stream buffer
			self.streamBuf.seek( 0 ); 
			self.streamBuf.truncate()

			# Request the cell info
			# note that a recv on the socket will block if a invalid
			# space is requested.
			# print "sending get_cells request..."
			if not self.s.send( struct.pack( "=cI", self.GET_CELLS,
											 self.space ) ):
				raise socket.error, "socket connection broken"
			# try: 
			# 	self.s.sendall( struct.pack( "=cI", self.GET_CELLS, self.space ))
			# except socket.error:
			# 	print "sendall on socket failed"
			# 	return None

		else:
			fetch = lambda n: streamBuf.read( n )

		# Read reply header
		dataLength, spaceID, self.appsTotal, self.numEntities = \
							struct.unpack( "iiii", fetch( 16 ) )
		stack = []
		self.root = None
		self.cells = {}

		while stack or not self.root:

			nodeType, = struct.unpack( 'b', fetch( 1 ) )
			shouldAppend = False

			# Leaf nodes (i.e. cellapps)
			if nodeType == 2:

				# Header
				ip, port, salt, load, appID, viewerPort = \
						struct.unpack( "IHHfIH", fetch( 18 ) )

				# Entity and chunk bounds
				numLevelsBuf = fetch( 4 )
				numLevels, = struct.unpack( "i", numLevelsBuf )

				# HACK: Check if this is 2.0 format where there is only a single
				# entity bounds rect
				if 0 < numLevels and numLevels < 100:
					numLevelsBuf = ""
				else:
					numLevels = 1

				entityBoundLevels = []
				for i in xrange( numLevels ):
					b = struct.unpack( "ffff",
							numLevelsBuf + fetch( 16 - len( numLevelsBuf ) ) )
					entityBounds = MFRectangle( b[0], b[2], b[1], b[3] )
					entityBoundLevels.append( entityBounds )

				b = struct.unpack( "ffff", fetch( 16 ) )
				chunkBounds = MFRectangle( b[0], b[2], b[1], b[3] )

				isRetiring = fetch( 1 ) != '\0'
				isOverloaded = fetch( 1 ) != '\0'
				addr = (ip, port)

				# Create object for cell and map it in
				newNode = LeafNode( addr, load, appID,
									viewerPort, entityBoundLevels, chunkBounds,
									isRetiring, isOverloaded )
				self.cells[ addr ] = newNode

			# Branch nodes
			elif nodeType in (0, 1):
				position, load, aggression = \
					struct.unpack( '<fff', fetch( 12 ) )
				newNode = BranchNode( position, load, aggression, nodeType == 0 )
				shouldAppend = True

			else:
				newNode = None

			if stack:
				if stack[-1].left == None:
					stack[-1].left = newNode
				else:
					stack[-1].right = newNode
					stack.pop()
			else:
				assert( not self.root )
				self.root = newNode

			if shouldAppend:
				stack.append( newNode )

		# If the post BSP dataLength is not 0, then we didn't get the full tree
		# somehow (very bad!)
		dataLength, = struct.unpack( "i", fetch( 4 ) )
		if dataLength != 0:
			raise RuntimeError, \
				  "Incomplete BSP read from socket (%d byte overflow)" % \
				  dataLength

		if not streamBuf:
			return self.streamBuf.getvalue()


	def getVersion( self ):
		msg = struct.pack( "=c", self.GET_VERSION )
		if not self.s.send( msg ):
			raise socket.error, "socket connection broken"

		stream = SocketFileWrapper( self.s )
		replyLen, = struct.unpack( "<I", stream.read( 4 ) )
		if (replyLen > 0):
			return struct.unpack( "<H", stream.read( 2 ) )
		else:
			return 0;


	def getSpaceGeometryMappings( self, spaceId = None ):
		
		if not spaceId:
			spaceId = self.space
		
		# Send request
		msg = struct.pack( "=cI", self.GET_SPACE_GEOMETRY_MAPPINGS, spaceId )
		if not self.s.send( msg ):
			raise socket.error, "socket connection broken"

		# Process response
		stream = SocketFileWrapper( self.s )
		return self.unpackSpaceGeometryMappingsMsg( stream )


	def unpackSpaceGeometryMappingsMsg( self, stream ):
		mappings = []

		msglen, = struct.unpack( "<I", stream.read( 4 ) )
		while (msglen > 0):
			key, = struct.unpack( "<H", stream.read( 2 ) )

			matrix = []
			matrix.append( struct.unpack( "<ffff", stream.read( 16 ) ) )
			matrix.append( struct.unpack( "<ffff", stream.read( 16 ) ) )
			matrix.append( struct.unpack( "<ffff", stream.read( 16 ) ) )
			matrix.append( struct.unpack( "<ffff", stream.read( 16 ) ) )

			strlen = BW_UNPACK3( stream )
			geometryPath = stream.read( strlen )

			mappings.append( (key, matrix, geometryPath) )

			msglen -= 2 + 16 + 16 + 16 + 16 + strlen
			if (strlen < 255):
				msglen -= 1
			else:
				msglen -= 4

		return mappings


	# --------------------------------------------------------------------------
	# Section: Private Methods
	# --------------------------------------------------------------------------

	def _getNBytes( self, n ):
		"""
		Read n bytes from the socket, and record everything that is read into
		self.streamBuf.
		"""

		toGet = n
		toRet = ''

		while toGet > 0:
			incoming = self.s.recv( toGet );
			if len( incoming ) == 0:
				raise socket.error, "socket connection broken"
				# return toRet
			toRet += incoming;
			toGet -= len( incoming )
			self.streamBuf.write( incoming )
		return toRet

# cell_app_mgr_talker.py
