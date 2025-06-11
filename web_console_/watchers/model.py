from sqlobject import *
from turbogears.database import PackageHub
from web_console.common import model

hub = PackageHub( "web_console" )
__connection__ = hub


class watcherFilters( model.DictSQLObject ):

	user = ForeignKey( "User", cascade = True )
	name = StringCol( length=64 )
	processes = StringCol( length=16 )
	path = StringCol( length=128 )


watcherFilters.createTable( True )
if not watcherFilters.select().count():
	print "Insert saved queries into the DB"
	watcherFilters( user = None, name="Received bytes",
					processes="cellapps",
					path="entityTypes/Avatar/properties/*/stats/received/*" )

	watcherFilters( user = None, name="Cells Overview",
					processes="cellapps",
					path="cells/*/*" )
