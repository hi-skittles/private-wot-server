"""
Library for retrieving scripts from various sources.

Also contains the RunScript base class.
"""

# Import standard modules
import os
import sys
import itertools
import socket
import logging

import simplejson

# Import pycommon modules
from pycommon import watcher_data_type as WDT, cluster
from pycommon import watcher_data_message

# Import webconsole modules
from web_console.common import util

log = logging.getLogger( "runscript" )

# -----------------------------------------------------------------------------
# Script management
# -----------------------------------------------------------------------------

scriptLoaders = {}

def registerScriptLoader( type, getScriptsFunc, getFromIdFunc, getCategoriesFunc ):
	"""
	Register a script loading function.

	Type is the identifier of the script loading source.
	e.g. for watcher scripts, the type is "watcher"

	loadFunc should take a string of the form "<type>:<arbitrary data>"
	as the argument and return a reference to the RunScript object.

	e.g. For watcher scripts, the string might be:
		watcher:cellapps:/scripts/printNumAvatars

	@param	getScriptsFunc		Function which loads scripts from a given category, given a category parameter
	@param	getCategoriesFunc	Function which retrieves categories
	"""
	global scriptLoaders
	scriptLoaders[type] = (getScriptsFunc, getFromIdFunc, getCategoriesFunc)

def getScript( id ):
	"""
	Given a string id, return the RunScript object.

	This function checks the first field of the id (which is a multi-
	element string separated by colons) which identifies the "type"
	of the script (atm, only "watcher" or "db" types used) and then
	passes it on to the appropriate script loader to actually construct
	and return the script object.

	@param id    The script ID, a string delimited by colons
	"""
	global scriptLoaders
	scriptType = id.split(":")[0]
	return scriptLoaders[scriptType][1]( id )

def getScriptsFromCategory( type, category ):
	"""
	Given a script type and category, return the list belonging to this
	category.

	@param type      The script "type" (watcher or db)
	@param category  The category from which we want to retrieve these scripts
	"""
	global scriptLoaders
	return scriptLoaders[type][0]( category=category )

def getCategories( type=None ):
	"""
	Given a script type, return the categories belonging to this type.

	@param type      The script "type" (watcher or db)
	"""
	global scriptLoaders
	categories = {}
	if type == None:
		for type, (_, _, getCategoriesFunc) in scriptLoaders.iteritems():
			categories[type] = getCategoriesFunc()
	else:
		categories[type] = scriptLoaders[type][2]()
	return categories

# -----------------------------------------------------------------------------
# RunScript base class
# -----------------------------------------------------------------------------
class RunScript( object ):
	"""
	Abstract RunScript object which represents a script that can be executed on the server.
	The most important method is the "execute" method, which runs the script.

	This class also contains constants and defaults which can be used in implementations
	of this class.
	"""
	type = None

	validRunTypes = ["all", "any"]
	validProcTypes = ["baseapp", "cellapp", "loginapp", "bots"]

	def __init__( self, id, title=None, code=None, args=None, procType=None,
			runType=None, desc=None, tags={} ):
		"""
		Base Runscript object.
		"""
		self.procType = procType
		self.runType = runType
		self.id = id
		self.title = title
		#self.tags = tags
		self.code = code
		self.args = args
		self.desc = desc

	def modify( self, *args ):
		pass

	def execute( self, args, output=None, runType=None ):
		pass

	def delete( self ):
		pass

	def info( self ):
		pass

	def copy( self ):
		pass

	def getDict( self ):
		return {
			"procType": self.procType,
			"runType": self.runType,
			"id": self.id,
			"title": self.title,
			"code": self.code,
			"args": self.args,
			"lockCells": self.lockCells,
			"desc": self.desc
		}

	def update( self, dct ):
		raise NotImplemented



	# -------------------------------------------------------------------------
	# Functions to process data from webpage form
	#
	# These functions are validation functions and conversion functions
	# -------------------------------------------------------------------------
	@classmethod
	def argsToJS( cls, args=[] ):
		"""
		Serialise an argument list in JSON format.
		Used to save argument list in a database as well as expose it via
		AJAX calls
		"""
		#print args
		return simplejson.dumps( cls.argsToStringList(args) )

	@classmethod
	def argsToStringList( cls, args=[] ):
		"""
		Give a list of (name, WatcherDataType) pairs, convert the
		WatcherDataType type objects to their respective ints.

		This is so the argument list can be easily serialised.

		e.g.
		[('numGuards', WatcherDataTypeInt)] to [('numGuards', 1)]
		[(None, WatcherDataTypeString)]     to [("", 5)]
		"""
		sl = [(n.value or "", t.value.type) for n,t in args]
		return sl

	@classmethod
	def initClassDicts( cls ):
		""" Initialise class dictionaries used in processing data from the
		create/edit script forms """

		# Add dictionaries to help process data from webpage
		cls.defaults = {
			"code" : "",
			"title":  "",
			"desc":  "",
			"worldReadable": False,
			"lockCells": False,
			"procType": "cellapp",
			"runType": "any",
			#"tags": {},
			"args": [],
			"argTypes": [] }

		# Add "filters" which convert things back from strings provided from
		# webpage forms to Python values. Some validation done here.
		cls.processors = {
			"code" : str,
			"title" : str,
			"desc" : str,
			"worldReadable" : cls.strToBool,
			"lockCells" : cls.strToBool,
			"procType": cls.isValidProcType,
			"runType" : cls.isValidRunType,
			}
		#log.debug( "Init class dicts!" )

	@classmethod
	def isValidProcType( cls, procType ):
		return procType.lower().replace(" ","") in cls.validProcTypes

	@classmethod
	def isValidRunType( cls, runType ):
		return runType.lower().replace(" ","") in cls.validRunTypes

	@staticmethod
	def strToBool( value ):
		if isinstance( value, bool ): return value
		return value.lower() in ["on", "true", "yes"]

	@staticmethod
	def makeList( value ):
		if hasattr( value, "__iter__" ): return value
		return ( value, )

	@staticmethod
	def isValidArgName( value ):
		if value == "":
			return False, "Name is empty"
		if not value[0].isalpha():
			return False, "First character must be alphanumeric"
		if not value.isalnum():
			return False, "Name must consist of only alphanumeric characters"
		return ( True, "" )

	@classmethod
	def processScriptData( cls, data ):
		"""
		To be used with the "edit/create script" forms which allow the user to
		enter manual scripts.

		Process the dictionary returned from the web page, and manipulates from
		pure string data to a more usable form.

		Also modifies the original dictionary to assign default values for those
		which didn't exist.
		"""
		processed = {}
		errors = []

		# Process single variables
		for key, processor in cls.processors.iteritems():
			try:
				if key not in data:
					data[key] = cls.defaults[key]
				processed[key] = processor( data[key] )
			except Exception, e:
				errors.append( "Error with %s: %s" % (key, str(e)) )

		# Process argument list
		data["args"] = cls.makeList( data.setdefault("args",[]) )
		data["argTypes"] = cls.makeList( data.setdefault("argTypes",[]) )
		processed["args"] = []
		if data.has_key("args"):
			for i, (name, type) in enumerate(
					itertools.izip( data["args"], data["argTypes"] ) ):
				valid, msg = cls.isValidArgName( name )
				if not valid:
					errors.append( "Error with argument %d: %s" % (i, msg))
				processed["args"].append(
						(name, WDT.WDTRegistry.getClass(int(type))) )
		else:
			processed["args"] = []

		data["jsArgs"] = cls.argsToJS( processed["args"] )
		return processed, errors

RunScript.initClassDicts()

# --------------------------------------------------------------------------
# Section: Helper classes
# --------------------------------------------------------------------------
class RunScriptOutput( dict ):
	""" A class which collects output resulting from running a script on the
	server """

	def __init__( self ):
		self["errors"] = []
		self["output"] = []
		self["result"] = []

	def addResult( self, result ):
		self["result"].append( result )

	def addOutput( self, output ):
		if output:
			self["output"].extend( output.splitlines() )

	def addErrorMessage( self, message, *args ):
		if args:
			message = message % args
		self["errors"].append( message )

	def __nonzero__( self ): return True

# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class ScriptException(Exception):
	pass

class ScriptCapabilityException(ScriptException):
	pass

class ScriptAttributeException(ScriptException):
	pass

class ScriptRunException(ScriptException):
	pass

import runscript_watcher
#import runscript_db
