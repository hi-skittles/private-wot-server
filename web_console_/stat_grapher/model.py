from sqlobject import *
from datetime import datetime
from turbogears.database import PackageHub
from turbogears import identity

from web_console.common import model

hub = PackageHub( "web_console" )
__connection__ = hub

class StatGrapherPrefs(  model.DictSQLObject ):
	class sqlmeta:
		table = "sg_prefs"
	user = ForeignKey( "User", cascade = True )
	log = StringCol( length=255 )
	displayPrefs = PickleCol( length=2**16, pickleProtocol=0 )

	RENAME_COLS = [('uid', 'user_id'),
	               ('uid_id', 'user_id')]

StatGrapherPrefs.createTable( True )
