from sqlobject import *
from datetime import datetime
from turbogears.database import PackageHub
from turbogears import identity
from web_console.common import model

hub = PackageHub( "web_console" )
__connection__ = hub

class ccStartPrefs( model.DictSQLObject ):

	user = ForeignKey( "User", cascade = True )
	last_mode = StringCol( length=10 )
	last_machine = StringCol( length=64 )
	last_layout = StringCol( length=64 )
	last_group = StringCol( length=64 )
	useTags = BoolCol()

	RENAME_COLS = [('uid', 'user_id'),
				   ('uid_id', 'user_id'),
				   ('mode', 'last_mode'),
				   ('arg', 'last_machine')]

	VERIFY_COLS = [('last_layout', 'varchar(64)'),
				   ('last_group', 'varchar(64)')]


class ccSavedLayouts( model.DictSQLObject ):

	user = ForeignKey( "User", cascade = True )
	name = StringCol()
	serveruser = StringCol()
	xmldata = StringCol()

	RENAME_COLS = [('uid', 'user_id'),
				   ('uid_id', 'user_id')]


### Custom Watcher Classes
class ccCustomWatchers( model.DictSQLObject ):

	user = ForeignKey( "User", cascade = True )
	pageName = StringCol( length=128 )
	uniqueIndex = DatabaseIndex( user, pageName, unique=True )


class ccCustomWatcherEntries( model.DictSQLObject ):

	# The Custom Watcher this entry belongs to
	customWatcherPage = ForeignKey( "ccCustomWatchers", cascade = True )

	# The component that contains the watcher value
	componentName = StringCol( length=128 )

	# The id number of the component to display
	# NB: For components that can have multiple instances running,
	#     a value of 0 indicates 'all active processes of this
	#     component type'.
	componentNumber = IntCol( default=0 )

	# The watcher value to query
	watcherPath = StringCol( length=256 )

	# Index to ensure the same watcher value only exists once per
	# custom layout.
	# Note: The watcher path index length has been set to 255 so that 3
	#       byte UTF-8 characters (used by MySQL) will fall within the key
	#       size limitation of 767 bytes imposed by MySQL.
	componentWatcherIndex = DatabaseIndex( customWatcherPage, componentName,
					{'column':watcherPath, 'length':255 }, unique=True )


class ccStartProcPrefs( model.DictSQLObject ):

	user = ForeignKey( "User", cascade = True )
	proc = StringCol( length=16, default = "" )
	machine = StringCol( length=40, default = "" )
	count = IntCol( default = 1 )


ccStartPrefs.createTable( True )
ccSavedLayouts.createTable( True )
ccStartProcPrefs.createTable( True )
ccCustomWatchers.createTable( True )
ccCustomWatcherEntries.createTable( True )
