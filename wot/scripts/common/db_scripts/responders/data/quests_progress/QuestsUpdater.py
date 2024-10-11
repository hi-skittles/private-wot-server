import ResMgr

import sqlite3

from db_scripts.responders.data.quests_progress.QuestsGetter import QuestsGetter
from bwdebug import TRACE_MSG


class QuestsUpdater:
	def __init__(self):
		self.getter = QuestsGetter()
	
	def update_quests_data(self, databaseID, key=None, value=None):
		"""
		Updates the quests data in the database using BigWorld.executeRawDatabaseCommand().
		"""
		raise DeprecationWarning("QuestsUpdater.update_quests_data :: This method is deprecated.")
		dbdir = ResMgr.resolveToAbsolutePath('scripts/db/quests/quests_db.sqlite')
		connection = sqlite3.connect(dbdir)
		cursor = connection.cursor()
		
		TRACE_MSG('QuestsUpdater.update_quests_data :: databaseID=%s, key=%s, value=%s' % (databaseID, key, value))
		command = "UPDATE quests_db SET ? = '?' WHERE dbid = ?"
		
		if key in ('potapovQuests', 'quests', 'tokens'):
			cursor.execute(command, (key, str(value), databaseID))
			connection.commit()
			connection.close()
		else:
			raise ValueError("QuestsUpdater.update_quests_data :: Invalid key provided. Must be one of 'potapovQuests', 'quests', or 'tokens'")
