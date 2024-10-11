import binascii
import BWTwoWay

def stringToVector( arg ):
	return tuple( float( s ) for s in arg.split(",") )

def utf8Decode( arg ):
	return arg.decode( 'utf-8' )

SIMPLE_CONVERTERS = dict(
	INT8  = int,
	INT16 = int,
	INT32 = int,
	INT64 = int,

	UINT8  = int,
	UINT16 = int,
	UINT32 = int,
	UINT64 = int,

	FLOAT32 = float,
	FLOAT64 = float,

	STRING = str,
	UNICODE_STRING = utf8Decode,
	BLOB = binascii.a2b_hex,

	VECTOR2 = stringToVector,
	VECTOR3 = stringToVector,
	VECTOR4 = stringToVector,
)

def simpleConvert( arg, argType ):
	converter = SIMPLE_CONVERTERS.get( argType )

	if not converter:
		raise TypeError( argType )

	return converter( arg )

def arrayConvert( allArgs, argName, argType ):
	result = []
	i = 0

	# First try with format ?myArray=4&myArray=5
	argList = allArgs.get( argName )
	if argList:
		return [simpleConvert( arg, argType ) for arg in argList]

	# Next try with format ?myArray[0]=4&myArray[1]=5
	while True:
		currArg = allArgs.get( "%s[%d]" % (argName, i ) )

		if currArg is not None:
			result.append( simpleConvert( currArg[0], argType ))
			i += 1
		else:
			return result


def convertArg( argList, allArgs, argType, argName ):
	try:
		if argList:
			return simpleConvert( argList[0], argType )
	except TypeError, e:
		pass

	typeParts = argType.split( ' ', 2 )

	if typeParts[0] in ("ARRAY", "TUPLE"):
		first, second = typeParts[1], typeParts[2]

		while first != 'of':
			first, second = second.split( ' ', 1 )

		if second.startswith( '(' ) and second.endswith( ')' ):
			second = second[1:-1]

		return arrayConvert( allArgs, argName, second )

	if not argList:
		raise BWTwoWay.BWInvalidArgsError(
				'Argument "%s" not specified' % (argName,) )
	else:
		raise BWTwoWay.BWInvalidArgsError(
				'Could not convert "%s" to %s for argument "%s"' %
				(argList, argType, argName) )


def convertArgs( args, argTypes ):
	"""Converts a dictionary that maps argument names to lists of strings to
	   values appropriate for passing to a method call."""

	typeDict = dict( argTypes )
	for arg in args:
		if not arg.split( '[', 1 )[0] in typeDict:
			raise BWTwoWay.BWInvalidArgsError( 'Unexpected argument "%s"' % arg )

	return tuple( convertArg( args.get( name, [] ), args, typeName, name )
				for name, typeName in argTypes )

# arg_convert.py
