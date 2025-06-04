import BigWorld
import pickle
import srvtest


from bwdecorators import functionWatcher, functionWatcherParameter
from snippet_decorator import testSnippet
from Math import Vector3
from copy import deepcopy

# -----------------------------------------------------------------------------
# Callable watcher for tests 

try:
	__snippetExposure = BigWorld.EXPOSE_BASE_SERVICE_APPS
except:
	try:
		__snippetExposure = BigWorld.EXPOSE_CELL_APPS
	except:
		__snippetExposure = BigWorld.EXPOSE_LOCAL_ONLY


@functionWatcher( "command/callTestSnippet",
		__snippetExposure,
		"Call a test snippet by name" )
@functionWatcherParameter( str, "Snippet function name" )
@functionWatcherParameter( str, "Arbitrary arguments" )
def callTestSnippet( snippetName, argsStr ):
	global _lastResult
	global _lastMark
	global _isWatcherAdded

	if not _isWatcherAdded:
		BigWorld.addWatcher( "testing/lastResult", _getLastResult )
		_isWatcherAdded = True

	try:
		_lastResult = ""
		_lastMark = ""
#		print "[bwtest] _lastMark = '%s'" % _lastMark 
#		print "[bwtest][info] callTestSnippet!"
#		print "[bwtest][info] Attempt to call snippet ", snippetName, " args = ", argsStr

		args = None
		try: 
			args = pickle.loads( argsStr )
		except:
			args = {}
#		print "[bwtest][info] Attempt to call snippet ", snippetName
		try:
#			print "[bwtest][info] snippets size = ", len(srvtest.testSnippets)
			snippet = srvtest.testSnippets[ snippetName ]
		except KeyError:
#			print "[bwtest][error] Snippet name %s not found" % snippetName
			return "error:"

#		print "[bwtest][info] Snippet ", snippetName, " found, calling... "
		res = snippet( **args )
		resStr = pickle.dumps( res )
#		print "[bwtest][info] callTestSnippet succeeded!"
		return "ok:" + resStr
	except Exception, e:
		return "error:" + str( e )


# -----------------------------------------------------------------------------
# These functions wrap writing the result to a standard testing watcher

_isWatcherAdded = False
_lastResult = ""
_lastMark = ""

def _getLastResult():
	global _lastResult
	global _lastMark

	result = _lastResult
	if result != "":
		_lastResult = ""
		_lastMark = ""
	else:
		result = "mark:" + _lastMark
	# print "[bwtest][info] getLastResult: ", result
	return result


def _setLastResult( result ):
	global _lastResult
	if _lastResult == "":
		if result:
			_lastResult = "pass:" + _lastMark
			# print "[bwtest][info] setLastResult: pass"
		else:
			_lastResult = "fail:" + _lastMark
			# print "[bwtest][info] setLastResult: fail"


def _addAssertMsg( msg ):
	if msg is None:
		return

	global _lastMark
	_lastMark += "\n" + str( msg )


def mark( msg ):
	global _lastMark
	_lastMark = str( msg )


def assertTrue( exp, msg = None ):
	if not bool( exp ):
		_addAssertMsg( msg )
		_setLastResult( False )


def assertFalse( exp, msg = None ):
	if bool( exp ):
		_addAssertMsg( msg )
		_setLastResult( False )


def assertEqual( a, b, msg = None ):
	if a != b:
		_addAssertMsg( msg )
		_setLastResult( False )


def assertNotEqual( a, b, msg = None ):
	if a == b:
		_addAssertMsg( msg )
		_setLastResult( False )


def fail( msg = None ):
	_addAssertMsg( msg )
	_setLastResult( False )


def vectorsToTuple( obj ):
	def processList( l ):
		for n, e in enumerate( l ):
			l[n] = vectorsToTuple( e )

	def processDict( d ):
		for k, v in d.items():
			d[k] = vectorsToTuple( v )

	if isinstance( obj, Vector3 ):
		return obj.tuple()

	elif isinstance( obj, list ):
		processList( obj )
		return obj

	elif isinstance( obj, tuple ):
		l = list( obj )
		processList( l )
		return tuple( l )

	elif isinstance( obj, dict ):
		processDict( obj )
		return obj

	else:
	 	return obj


def finish( res = None ):
	global _lastMark

	# Convert Vector3s to tuples as they can't be pickled
	resCpy = deepcopy( res )
	resCpy = vectorsToTuple( resCpy )

	_lastMark = pickle.dumps ( resCpy )
	_setLastResult( True )
