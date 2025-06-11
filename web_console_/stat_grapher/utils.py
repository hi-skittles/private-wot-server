"""
Generic utility functions used by StatGrapher
"""

# Import standard modules
import time
import inspect
import socket
import struct

# Import third party modules
from turbogears import view

# -------------------------------------------------------
# Section: Kid template utility functions
# -------------------------------------------------------

# A "formatTime" utility function for use in kid templates
def formatTime( t ):
	"""Given a float or integer, return a formatted time string"""
	return time.strftime( "%d %b %Y, %H:%M:%S", time.localtime( int(t) ) )

# Function to pass to variableProviders in order to make thigns
# available in the templates
def addVariables( variables ):
	global staticDirectory
	variables['formatTime'] = formatTime

def setup():
	view.variable_providers.append( addVariables )

# -------------------------------------------------------
# Section: Function logging utilities
# -------------------------------------------------------
# Utility global var for below
logFuncCallLevel = -1

# Function timer decorator
def logFunc( logMethod, logStart=True, name=None ):
	"""
	Decorator function which writes the function execution time
	to a given log method. If logStart is True then the decorator
	will also write the beginning of the function to the log method.
	"""
	def decorator( f ):

		# Determine name of function
		if name == None:
			funcName = f.__name__
		else:
			funcName = name

		# Create decorator
		def _wrapper( *args, **kwargs ):
			global logFuncCallLevel
			logFuncCallLevel += 1
			funcStart = time.time()
			if logStart:
				logMethod( "%sCalling %s", " "*logFuncCallLevel, funcName )
			try:
				result = f( *args, **kwargs )
				logMethod( "%sCalled  %s (%.3fs)", " "*logFuncCallLevel,
					funcName, time.time() - funcStart )
				logFuncCallLevel -= 1
			except Exception, e:
				logMethod( "%sCalled  %s (%.3fs) (Exception thrown)",
					" "*logFuncCallLevel, funcName, time.time() - funcStart )
				logFuncCallLevel -= 1
				raise
			return result
		return _wrapper
	return decorator

# Print arguments of the function
def logArgs( logMethod, name=None ):
	frame = inspect.stack()[1]
	argValues = inspect.getargvalues( frame[0] )
	argList = []

	for n in argValues[0]:
		#try:
		#	argList.append( "%s=%s" % (n, argValues[-1][n].__repr__() ) )
		#except:
			argList.append( "%s=%s" % (n, argValues[-1][n] ) )

	# Determine name of function
	if name == None:
		funcName = frame[3]
	else:
		funcName = name

	logMethod( "Arguments for %s: (%s)", funcName, ",".join( argList ) )


# MySQL query timer
def timeQuery( logMethod, desc, cursor, query, *args, **kwargs ):
	"""
	Executes an SQL query and writes the query string and time taken
	to the specified log method.

	Params:
		logMethod: Logging object method to call
		desc:	   Description of query
		cursor:	   MySQLdb cursor object
		query:	   Query string, MySQLdb style
		args:	   Any arguments to insert into the query string
	"""

	# This part is very hacky, and if MySQLdb ever changes
	# the Cursor class methods this may cease to work
	db = cursor._get_db()

	if args != None:
		queryString = query % db.literal( args )
	else:
		queryString = query

	printSQL = kwargs.get( "printSQL", False )
	threshold = kwargs.get( "threshold", 1.0 )
	lowerThreshold = kwargs.get( "lowerThreshold", 0.01 )

	if printSQL:
		logMethod( "%s: %s", desc, queryString )

	queryStart = time.time()
	results = cursor.execute( queryString )

	timeTaken = time.time() - queryStart

	if threshold and timeTaken > 1.0:
		if not printSQL:
			logMethod( "%s: %s", desc, queryString )
		logMethod( "WARNING: %s took (%.3fs, %d rows)", desc,
			timeTaken, cursor.rowcount )
	else:
		if (printSQL) or (lowerThreshold == None) or \
			(timeTaken > lowerThreshold):
			logMethod( "%s finished (%.3fs, %d rows)", desc,
				timeTaken, cursor.rowcount )

	return results

# -------------------------------------------------------
# Section: Miscellaneous functions
# -------------------------------------------------------

def inet_ntoa( ipNum ):
	"""Return the text of the given integer IP address."""
	return socket.inet_ntoa( struct.pack( '@I', ipNum ) )

def inet_aton( ipString ):
	"""
	Return integer IP address given its string representation as a dotted
	quad.
	"""
	return struct.unpack( '@I', socket.inet_aton( ipString ) )[0]
