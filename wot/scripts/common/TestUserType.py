import struct

class TestType:
	def __init__( self, a, b, c ):
		# integer
		self.a = a
		# string
		self.b = b
		# list of floats
		self.c = c

class StreamUnpacker:
	def __init__( self, stream ):
		self._stream = stream
		self._offset = 0

	def unpack( self, format ):
		len = struct.calcsize( format )
		return struct.unpack( format, self.data( len ) )

	def data( self, dataLen ):
		if self._offset + dataLen > len( self._stream ):
			raise IndexError
		slice = self._stream[self._offset:self._offset + dataLen]
		self._offset += dataLen
		return slice

class TestUserTypeWrapper:
	def addToStream( self, obj ):
		#print "addToStream"
		out = struct.pack( "ib", obj.a, len( obj.b ) )
		out += obj.b
		if len( obj.c ) < 0xFF:
			out += struct.pack( "B", len( obj.c ) )
		else:
			out += struct.pack( "i", ( len( obj.c ) << 8 ) | 0xFF )

		for v in obj.c:
			out += struct.pack( "f", v )
		return out

	def createFromStream( self, stream ):
		#print "createFromStream"
		packed = StreamUnpacker( stream )
		a, lenB = packed.unpack( "ib" )
		b = packed.data( lenB )

		lenC = packed.unpack( "B" )
		if lenC == 0xFF:
			lenC0, lenC1, lenC2 = packed.unpack( "BBB" )
			lenC = lenC0 | lenC1 << 8 | lenC2 << 16

		c = list( packed.unpack( "%df" % lenC ) )
		return TestType( a, b, c )

	def addToSection( self, obj, section ):
		#print "addToSection"
		section.createSection( 'a' )
		section['a'].asInt = obj.a
		section.createSection( 'b' )
		section['b'].asString = obj.b
		section.createSection( 'c' )
		# obj.c is usually a list, needs to be a tuple for writeFloats
		section['c'].writeFloats( "item", tuple( obj.c ) )

	def createFromSection( self, section ):
		#print "createFromSection"
		a = section['a'].asInt
		b = section['b'].asString
		c = list( section['c'].readFloats( "item" ) )
		return TestType( a, b, c )

	def fromStreamToSection( self, stream, section ):
		#print "fromStreamToSection"
		o = self.createFromStream( stream )
		self.addToSection( o, section )

	def fromSectionToStream( self, section ):
		#print "fromSectionToStream"
		o = self.createFromSection( section )
		return self.addToStream( o )

	def defaultValue( self ):
		#print "defaultValue"
		return TestType( 32, "TestType", [3., 4., 5.] )

	def bindSectionToDB( self, binder ):
		#print "bindSectionToDB"
		binder.bind( 'a', "INT32" )
		binder.bind( 'b', "STRING" )
		binder.bind( 'c', "ARRAY<of>FLOAT</of>" )

instance = TestUserTypeWrapper()
