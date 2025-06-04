
import srvtest
import watcher

class testSnippet( object ):
	""" Decorator for a remotely callable snippet """

	def __init__( self, func ):
		self._func = func
		if not hasattr( srvtest, "testSnippets" ):
			srvtest.testSnippets = {}
			# print "[bwtest] Created srvtest.testSnippets dict"

		srvtest.testSnippets[ func.__name__ ] = self.__call__
		# print "[bwtest] added snippet ", func.__name__


	def __call__( self, *args, **kwArgs ):
#		print "[bwtest] testSnippet decorator called: ", self._func.__name__
		srvtest.mark( "Test snippet '%s'" % self._func.__name__ )
		try:		
			return self._func( *args, **kwArgs )
		except:
			srvtest.assertTrue( False )
			raise


class testStep( object ):
	""" Decorator for a test step.
		It handles the exceptions as failures."""
		
	def __init__( self, func ):
		self._func = func
		self._mark = func.__name__

	def __call__( self, *args, **kwArgs ):
		srvtest.mark( "Test step '%s'" % self._mark )
		try:		
			return self._func( *args, **kwArgs )
		except:
			srvtest.assertTrue( False )
			raise

#------------------------------------------------------------------------------
# Sample snippets for testing

@testSnippet
def selfTestSnippetNoArg():
	# print "[bwtest] Called selfTestSnippetNoArg"
	srvtest.finish()
	return


@testSnippet
def selfTestSnippetWithArg( arg1, arg2 ):
	# print "[bwtest] Called selfTestSnippetWithArg, args = ", arg1, arg2
	srvtest.assertEqual( arg1, 1 )
	srvtest.assertEqual( arg2, "test" )
	srvtest.finish()
	return
