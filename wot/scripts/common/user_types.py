import struct

class UserType1( object ):
	def addToStream( self, obj ):
		return struct.pack( "if", *obj )


	def createFromStream( self, stream ):
		return struct.unpack( "if", stream )


	def bindSectionToDB( self, binder ):
		binder.bind( "intVal", "INT32" )
		binder.bind( "floatVal", "FLOAT32" )


	def defaultValue( self ):
		return (0, 0.0)


userType1 = UserType1()

class MyObj2( object ):
	def __init__( self, intVal, arrayVal ):
		self.intVal = intVal
		self.arrayVal = arrayVal


	def __str__( self ):
		return "MyObj2.str: %r %r" % (self.intVal, self.arrayVal)


	def __repr__( self ):
		return "MyObj2.repr: %r %r" % (self.intVal, self.arrayVal)


	def __cmp__( self, other ):
		return cmp( self.intVal, other.intVal ) or \
			cmp( self.arrayVal, other.arrayVal )


class UserType2( object ):
	def addToStream( self, obj ):
		if len( obj.arrayVal ) < 0xFF:
			return ''.join(
				(struct.pack( 'iB', obj.intVal, len( obj.arrayVal ) ),
				''.join( struct.pack( 'i', val ) for val in obj.arrayVal )) )

		return ''.join(
			(struct.pack( 'ii', obj.intVal, 
				( len( obj.arrayVal ) << 8 ) | 0xFF ),
			''.join( struct.pack( 'i', val ) for val in obj.arrayVal )) )


	def createFromStream( self, stream ):
		intVal, arrayLen = struct.unpack( 'iB', stream[0:5] )
		if arrayLen == 0xFF:
			arrayLen = ( struct.unpack( "i", stream[4:8] ) >> 8 )

		arrayVal = [ struct.unpack( 'i', stream[8+4*i : 12+4*i] )[0]
												for i in range( arrayLen ) ]

		return MyObj2( intVal, arrayVal )


	def bindSectionToDB( self, binder ):
		binder.bind( "intVal", "INT32" )
		binder.beginTable( "arrayVal" )
		binder.bind( "value", "INT32" )
		binder.endTable() # subTable


	def defaultValue( self ):
		return MyObj2( 0, [] )

userType2 = UserType2()

# user_types.py
