from sqlobject import *
from datetime import datetime
from turbogears.database import PackageHub
from turbogears import identity

import bwsetup; bwsetup.addPath( "../.." )
from web_console.common import model
from pycommon import util

from pycommon import bwlog as bwlog_module
bwlog = bwlog_module._bwlog

hub = PackageHub( "web_console" )
__connection__ = hub

def getSeverityList():
	return ",".join( [s for s, n in sorted( bwlog.SEVERITY_LEVELS.items(),
											key = lambda (s,n): n )] )

class lvQuery( model.DictSQLObject ):

	user = ForeignKey( "User", cascade = True )

	# This is the user-assignable name for the query
	name = StringCol( length=256 )

	# serialised query filters/params
	query_string = StringCol( length=1024, default = "" )

	VERIFY_COLS = [ ("query_string", "varchar(1024)") ]

	class sqlmeta:
		createSQL = { 'mysql' : [
			"ALTER TABLE lv_query CONVERT TO CHARACTER SET utf8" ]
		}
	# class sqlmeta

# class lvQuery


class lvAnnotation( model.DictSQLObject ):

	user = ForeignKey( "User", cascade = True )
	message = StringCol()

# model.py
