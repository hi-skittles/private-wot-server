customFactories = {}
import exceptions

def addCustomError( exc ):
	# print "BWTwoWay.addCustomError:", exc
	customFactories[ exc.__name__ ] = exc

class BWError( Exception ):
	pass

class BWMetaCustomError( type ):
	def __new__( mcs, name, bases, dict ):
		klass = type.__new__( mcs, name, bases, dict )
		addCustomError( klass )
		return klass

class BWCustomError( BWError ):
	# Any class derived from BWCustomError automatically registers itself as a
	# custom error.
	__metaclass__ = BWMetaCustomError
	pass

class BWStandardError( Exception ):
	pass

class BWMercuryError( BWStandardError ):
	pass

class BWInternalError( BWStandardError ):
	pass

class BWInvalidArgsError( BWStandardError ):
	pass

class BWNotFoundError( BWStandardError ):
	pass

class BWNoSuchEntityError( BWStandardError ):
	pass

class BWNoSuchCellEntityError( BWStandardError ):
	pass

class BWAuthenticateError( BWStandardError ):
	pass

class BWFileOpenError( BWStandardError ):
	pass

class BWFinaliseError( BWStandardError ):
	pass

def createError( excType, args ):
	# Built-in exceptions are currently streamed as exceptions.ValueError, etc.
	excType = excType.split( '.' )[-1]
	excClass = getattr( exceptions, excType, None )

	if not excClass:
		excClass = globals().get( excType )

	if not excClass:
		excClass = customFactories.get( excType )

	if not excClass:
		print "BWTwoWay.createError: Defaulting '%s' to Exception" % excType
		excClass = Exception

	if not issubclass( excClass, Exception ):
		print "Error: BWTwoWay.createException: '%s' is not an Exception" % str( excClass )
		return Exception( args )

	return excClass( *args )

# BWTwoWay.py
