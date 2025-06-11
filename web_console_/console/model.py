from sqlobject import *
from datetime import datetime
from turbogears.database import PackageHub
from turbogears import identity
import web_console.common.model

hub = PackageHub( "web_console" )
__connection__ = hub

class RunScript( web_console.common.model.DictSQLObject ):
	""" Object representing a runscript script """
	class sqlmeta:
		table = "run_script"
	#name = StringCol( length=100, alternateID=True )
	title = StringCol( length=100, alternateID=True )
	description = StringCol( length = 1000 )
	code = StringCol()
	worldReadable = BoolCol()
	lockCells = BoolCol()
	procType = StringCol( length=20 )
	runType = StringCol( length=20 )
	modified = DateTimeCol()
	user = ForeignKey( "User", cascade = True )
	args = StringCol()
#	tags = MultipleJoin( "RunScriptTags", joinColumn="run_script_id" )

# class RunScriptTags( web_console.common.model.DictSQLObject ):
# 	""" Object representing a single tag """
# 	class sqlmeta:
# 		table = "run_script_tags"
# 	runScript = ForeignKey( "RunScript" )
# 	tag = StringCol()
# 	value = StringCol()

RunScript.createTable( True )
#RunScriptTags.createTable( True )
