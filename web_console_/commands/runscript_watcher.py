import logging

# Import web console modules
from web_console.common import util

from pycommon import cluster, watcher_data_type as WDT
from pycommon import watcher
from pycommon import watcher_data_message, watcher_call
from pycommon.watcher_call import WatcherCall

# Import local modules
import runscript

log = logging.getLogger("runscript")

# -----------------------------------------------------------------------------
# Watcher script class
# -----------------------------------------------------------------------------
class WatcherRunScript( runscript.RunScript ):
	"""
	Class which represents a script exposed through watchers on a
	cellapp/baseapp/loginapp/bots.

	Contains functionality for retrieving information about Watcher functions
	as well as executing these scripts.
	"""

	def __init__( self, watcherCall, runType="any", 
				args=None, desc=None ):
		"""
		@param watcherCall  The underlying WatcherCall to wrap.
	
		@param runType      The method which determines how the script is run.
							Valid values are: "any", "all".
							Note that "any" will result in the script being
							called on the least loaded component.
		@param args         A list containing (name, WatcherDataType) tuple
		                    pairs. This list is mostly for user interface
                            purposes and can be used for validating that
                            function arguments are of the right type.
                            Optional parameter.
		@param desc         The script description. Should correspond to the
		                    __doc__ watcher attribute.

		The constructor only requires the minimum amount of information
		to run. That is, only the target and watcherPath is required.
		"""

		procType    = watcherCall.procType
		watcherPath = watcherCall.watcherPath
		scriptName  = watcherPath[watcherCall.watcherPath.rfind( '/' ) + 1:]

		runscript.RunScript.__init__( self,
			id     = ":".join( ("watcher", procType, runType, watcherPath) ),
			title  = scriptName,
			code   = None,
			args   = args,
			desc   = desc,
			procType = procType,
			runType = runType,
		)

		self.watcher  = watcherCall
		self.args     = None
		self.desc     = None
		self.procType = None 
		self.runType  = runType 

	def execute( self, args, output=None, runType=None ):
		return self.watcher.execute( args, output )

	def retrieveInfo( self ):
		self.watcher.retrieveInfo()
		self.args     = self.watcher.args
		self.desc     = self.watcher.desc
		self.procType = self.watcher.procType 
		self.runType  = self.watcher.runType


# -----------------------------------------------------------------------------
# General functions
# -----------------------------------------------------------------------------

def getCategories( user=None ):
	"""
	Retrieve the set of categories that watcher scripts use.

	For watcher scripts, categories are defined by any watcher directory entries
	under the "commmand" top level directory on any
	baseapp/cellapp/loginapp/bots. It is assumed that each
	baseapp/cellapp/loginapp/bots contains the same set of Watcher functions
	(in normal use they shouldn't carry different functions, although sometimes
	the server can get into a bad state where it does).
	"""
	if not user:
		c = cluster.cache.get()
		user = util.getUser( c )
	path = "command"
	procs = []
	cellapp = user.getProc("cellapp")
	baseapp = user.getProc("baseapp")
	loginapp = user.getProc("loginapp")
	bots = user.getProc("bots")
	procs = [p for p in (baseapp, cellapp, loginapp, bots) if p != None]
	dirs = [""]
	if procs:
		response = watcher_data_message.WatcherDataMessage.batchQuery( [path], procs, 2 )
		#print "Response", response
		for p, listing in response.iteritems():
			#print "Listing:", listing
			if path in listing:
				dirs.extend( [l[0] for l in listing[path] if l[3] == \
					watcher_data_message.WatcherDataMessage.WATCHER_MODE_DIR] )
	#print "Categories:", dirs
	return dirs


def getScripts( category, user=None ):
	"""
	Retrieve a list of watcher scripts from a baseapp/cellapp/loginapp/bots
	(the first baseapp/cellapp/loginapp/bots process found is the one queried).

	If a category is specified, then we retrieve Watcher functions in the
	directory corresponding to that category. If category is a blank string,
	then get the list of Watcher functions directly under the top level
	"command" directory.

	NOTE: The resulting script objects do NOT contain the following attributes:
		- args (the argument list consisting of (name, WatcherDataType) pairs)
		- desc (the description string)

	To get these attributes you need to call the "retrieveInfo" method on the
	watcher object which will then fill in these attributes.

	@param category The category for which we want the list of scripts.
                    Corresponds to a directory under the top level "command"
					directory on the baseapp/cellapp/loginapp/bots.
	@param user     User object for who we want the scripts.
	"""

	if not user:
		c = cluster.cache.get()
		user = util.getUser( c )
	# Scan baseapp, cellapp, loginapp, bots
	retScripts = []
	for watcher in watcher_call.watcherFunctions( category, user ):
		retScripts.append( WatcherRunScript( watcher ) )

	return retScripts


def getScript( id ):
	"""
	Given an ID string, create a RunScript script object that we can then
	run methods on. No remote watcher queries are made as a result of this
	function.

	NOTE: The resulting script objects do NOT contain the following attributes:
		- args (the argument list consisting of (name, WatcherDataType) pairs)
		- desc (the description string)

	To get these attributes you need to call the "retrieveInfo" method on the
	watcher object which will then fill in these attributes.

	@param id	The ID is of the format "watcher:<proctype>:<runtype>:<watcherPath>"
				e.g. "watcher:baseapp:any:command/numEntities"
				e.g. "watcher:baseapp:1,2:command/addGuards"
				e.g. "watcher:cellapp:all:command/createStorm"
	"""

	c = cluster.cache.get()
	user = util.getUser( c )

	_, procType, runType, path = id.split( ":", 3 )

	watcher = WatcherCall( user, path, procType )
	return WatcherRunScript( watcher, runType=runType )



runscript.registerScriptLoader( "watcher", getScripts, getScript, getCategories )
