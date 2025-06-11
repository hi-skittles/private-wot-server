# Import standard modules
from datetime import datetime
from StringIO import StringIO
import os
import fnmatch
import logging

# Import third party modules
from turbogears.controllers import (RootController, expose, error_handler,
                                    flash, redirect, validate)
from turbogears import identity
import turbogears
from sqlobject import AND, OR, SQLObject
import sqlobject
import cherrypy
import simplejson

# Import BigWorld modules
import bwsetup; bwsetup.addPath( "../.." )
from web_console.common import ajax
from web_console.common import module
from web_console.common import util
from web_console.common.model import User
from web_console.common.authorisation import Permission
from pycommon import cluster, watcher_data_type as WDT

# Import local modules
# Currently not saving anything to the DB
#import model
import runscript
#import runscript_db

log = logging.getLogger( __name__ )

# --------------------------------------------------------------------------
# Section: Python console
# --------------------------------------------------------------------------
class Commands( module.Module ):

	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )
		self.addPage( "Library", "run" )
		self.addPage( "Help", "help" )

#		# Reload scripts from file
#		try:
#			self.loadScriptsFromDir()
#			self.removeDeletedScripts()
#			self.loadScriptFail = False
#		except Exception, e:
#			self.loadScriptFail = True


	# --------------------------------------------------------------------------
	# Section: Runscript
	# --------------------------------------------------------------------------
	@identity.require( Permission( 'view', 'modify' ) )
	@expose( template="commands.templates.run" )
	def run( self, id=None ):
		"""
		WebConsole page which presents an interface for select a script to run
		and actually running it.

		@param id    ID of a script to execute straight away.
		             TODO: Get it working again, as it's currently not.
					 This will be done in runscript.kid and runscript.js.

					 However you'll need to pass an argument value list
					 to for scripts which take arguments. The alternative
					 is not to have the script execute straight away, but
					 simply just to show up, ready for the user to enter
					 argument values and execute.
		"""
		c = cluster.cache.get()
		user = util.getUser( c )
		livingProcs = user.getServerProcs()

		# if there is still process alive, we assume server is running
		isServerRunning = ( len( livingProcs ) > 0 )

		# Scripts are provided in a tree structure
		categories = runscript.getCategories()
		return dict(
			categories = categories,
			runNow = None,
			serverRunning = isServerRunning 
		)


	@identity.require( Permission( 'view', 'modify' ) )
	@expose( allow_json=True )
	def executescript( self, id=None, args=None, runType=None ):
		"""
		AJAX interface for executing a script.

		@param id    The string ID of the script that needs to be run.
		@param args  The JSON encoded list of arguments of the format:
			         [(value, WatcherTypeEnum), ...]
			         e.g. [(100, 1), ('hello', 5)]
		             The WatcherTypeEnum will be used to parse the value from
					    string format to a more appropriate format.
		@param runType  The method by which the server will be run. Typically
		                mirrors the RunScript.runType attribute, but can be
						overridden from the webpage. Possible values are:
						"all", "any", or a comma-delimited list of ints
		"""
		args = simplejson.loads( args )
		script = runscript.getScript( id );
		if runType != None:
			runType = runType.encode( "utf8" )

		argList = []
		argCount = 0
		canExecute = True
		output = runscript.RunScriptOutput()
		for value, valueType in args:
			argCount += 1

			if not len(value) and valueType != WDT.WATCHER_TYPE_STRING:
				output.addErrorMessage( "Argument %d: No value provided.",
					argCount )
				canExecute = False
				continue

			try:
				# TODO:
				#
				# More sensible conversion of the argument values from
				# strings to WatcherDataTypes
				#
				# e.g. At the moment a WatcherDataTypeBool is created simply
				# by passing the string through "bool()", which returns
				# True on nonempty strings regardless of content.
				#
				wdt = WDT.WDTRegistry.getClass( valueType )(
						value.encode( "utf8" ) )
				argList.append( wdt )
			except Exception, e:
				output.addErrorMessage( "Argument %d: Couldn't convert \"%s\"" \
					" to %s: %s",
					argCount, value, WDT.toString( valueType ), e )
				canExecute = False


		if canExecute:
			try:
				script.execute( argList, output, runType )
			except Exception, e:
				output.addErrorMessage( "Error running script: %s: %s",
					type(e), e )
				raise
		#print "Output: %s" % (output)
		return {"output": output}

	@identity.require( Permission( 'view' ) )
	@expose( allow_json=True )
	def scriptinfo( self, id=None ):
		"""
		AJAX interface for retrieving information about a script.
		Returns a dictionary containing the following key/values:
			- title: Script title
			- procType: Type of component the script runs on
			- runType: Method by which the script should be run.
			- desc: Description of the script.
			- args: JSON encoded argument list

		@param id   The string ID of the script.
		"""

		if isinstance( id, unicode ):
			id = id.encode( "utf8" )

		script = runscript.getScript( id )
		script.retrieveInfo()
		return {
			"title": script.title,
			"procType": script.procType,
			"runType": script.runType,
			"desc": script.desc,
			"args": script.argsToStringList( script.args ),
		}

	@identity.require( Permission( 'view' ) )
	@expose( allow_json=True )
	def getscripts( self, type, category ):
		"""
		AJAX interface for retrieving a list of scripts belonging to a
		category.

		@param type      The source of the scripts that the category belongs to
		@param category  The name of the category from we want the list of
		                 scripts
		"""
		type = type.encode( "utf8" )
		category = category.encode( "utf8" )
		scriptList = runscript.getScriptsFromCategory( type, category )
		scripts = [{"id":s.id, "title":s.title} for s in scriptList]
		return {"scripts": scripts}


	# --------------------------------------------------------------------------
	# Section: Runscript utility functions
	# --------------------------------------------------------------------------
	def getScriptActions( self, script ):
		""" Creates an appropriate ActionMenuOptions object for a script.  """
		user = util.getSessionUser()
		actions = util.ActionMenuOptions()

		actions.addRedirect( "Run",
				turbogears.url( "/console/runscript", id = script.id ),
				help = "Run this script" )

		if script.user == user:
			actions.addRedirect( "Edit",
				"/console/editscript?action=edit&id=%s" % (script.id),
				help="Edit this script" )

			actions.addScript( "Delete",
				"""
				var goAhead=confirm(
					"Are you sure you want to delete script '%s'?");
				if (goAhead) {window.location="/console/deletescript?&id=%s";}
				""" % (script.title, script.id),
				help="Delete this script" )

			actions.addRedirect( "Duplicate",
					turbogears.url( "/console/dupscript", id = script.id ),
					help = "Make a copy of this script" )

		if script.user != user:
			actions.addRedirect( "View source",
					"/console/viewscript?id=%s" % (script.id),
					help="View script source" )

		return actions

	def blankScriptDict( self ):
		""" Returns a blank script dictionary """
		return dict( title="", worldReadable=False, lockCells=False,
			procType="cellapp", runType="any", code="", desc="", jsArgs=[])



	def runWatcherScript( self, procName, watcher, code, output=None ):
		c = cluster.cache.get()
		user = util.getUser( c ) # Cluster.User object
		proc = user.getProc( procName )
		if proc == None:
			raise ScriptRunException( "No %s available to run the script. Is the server running?" % \
				(procName) )

		if output: output.info( "Retrieved %s on %s(%s)" , proc.label(),
			proc.machine.name, proc.machine.ip )

		# Check we have processes to run it on
		childProcs = {"baseappmgr": "baseapp", "cellappmgr": "cellapp"}
		procs = user.getProcs( childProcs.get( procName, procName ) )
		if not procs:
			output.warning( "There are no %ss, so this script will " \
				"probably have no effect.", childProcs[procName] )

		code = code.replace('\r\n', '\n')
		result = proc.setWatcherValue( watcher, code )
		if output: output.info( "Executed script!" )
		return result

	# --------------------------------------------------------------------------
	# Section: Misc
	# --------------------------------------------------------------------------
	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self ):
		raise redirect( "run" )

