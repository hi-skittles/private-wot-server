from datetime import datetime

from web_console.common import util
from sqlobject import OR, AND
import simplejson

from pycommon import watcher_data_type as WDT

import runscript
import model

# -----------------------------------------------------------------------------
# DbRunScript class
# -----------------------------------------------------------------------------
class DbRunScript( runscript.RunScript ):
	"""
	Wrapper around model.RunScript to conform to the runscript.RunScript
	base class.
	"""
	type="db"

	def __init__( self, dbObj, args=None ):

		if args == None:
			args = [(n, WDT.WDTRegistry.getClass(t)) for n,t in \
				simplejson.loads( dbObj.args )]
		runscript.RunScript.__init__( self,
			id     =  ":".join( ("db", str(dbObj.id) ) ),
			title  = dbObj.title,
			code   = dbObj.code,
			procType = dbObj.procType,
			runType  = dbObj.runType,
			args   = args,
			#tags   = dict( (t.tag, t.value) for t in dbObj.tags ),
			desc   = dbObj.description,
		)
		self.lockCells = dbObj.lockCells,
		self.worldReadable = dbObj.worldReadable,
		self.modified = dbObj.modified
		self.user = dbObj.user
		self.dbObj = dbObj

	def execute( self ):
		pass

	def getDict( self ):
		"""
		Gets the dictionary of relevant attributes, and appends DbRunScript
		specific attributes as well...
		"""
		d = runscript.RunScript.getDict( self )
		d["worldReadable"] = self.worldReadable
		d["lockCells"] = self.lockCells
		return d

	def update( self, dct ):
		"""
		Updates not only the object, but the underlying object
		as well.
		"""
		if "title" in dct:
			self.dbObj.title = dct["title"]
			self.title = dct["title"]
		if "code" in dct:
			self.dbObj.code = dct["code"]
			self.code = dct["code"]
		if "procType" in dct:
			self.dbObj.procType = dct["procType"]
			self.procType = dct["procType"]
		if "runType" in dct:
			self.dbObj.runType = dct["runType"]
			self.runType = dct["runType"]
		if "args" in dct:
			self.dbObj.args = self.argsToJS( dct["args"] )
			self.args = dct["args"]
		if "desc" in dct:
			self.dbObj.desc = dct["desc"]
			self.desc = dct["desc"]
		if "worldReadable" in dct:
			self.dbObj.worldReadable = dct["worldReadable"]
			self.worldReadable = dct["worldReadable"]
		if "lockCells" in dct:
			self.dbObj.lockCells = dct["lockCells"]
			self.lockCells = dct["lockCells"]

	@classmethod
	def createScript( cls, title, code, args, worldReadable, lockCells, procType,
			runType, desc="", modified=None, tags={}, **kwargs ):
		"""
		Creates a script and saves it in the database

		@return		Reference to the new DbRunScript object.
		"""
		user = util.getSessionUser( )
		modified = modified or datetime.now()
		scriptObj = model.RunScript(
			title=title,
			code=code,
			args = cls.argsToJS( args ),
			worldReadable = worldReadable,
			lockCells = lockCells,
			procType = procType,
			runType = runType,
			description = desc,
			modified = modified,
			user = user
		)
		#for t,v in tags:
		#	newTag = model.RunScriptTag( tag=t, value=v, runScript=newDbScript )
		newScript = DbRunScript( scriptObj, args=args )
		return newScript

# -----------------------------------------------------------------------------
# General functions
# -----------------------------------------------------------------------------

def getCategories( user=None ):
	"""
	Retrieve categories of watcher scripts
	"""
	return [""]

def getScripts( category=None, userOnly=True ):
	"""
	Retrieve scripts from the database. Ignores those which were loaded
	from a file.

	@param force	Unused parameter
	"""
	user = util.getSessionUser()

	if userOnly:
		scriptQuery = model.RunScript.select(
			model.RunScript.q.userID == user.id )
	else:
		scriptQuery = model.RunScript.select(
			OR( model.RunScript.q.userID == user.id,
				model.RunScript.q.worldReadable == True ) )
	scripts = list( DbRunScript(s) for s in scriptQuery )
	return scripts

def getScript( id ):
	"""
	Retrieve a particular script, given an id.
	ID is of the format "db:<scriptid>"

	Example ID:
		db:12
	"""
	_, dbId = id.split( ":", 1 )
	dbObj = model.RunScript.get( dbId )
	return DbRunScript( dbObj )

runscript.registerScriptLoader( "db", getScripts, getScript, getCategories )
