import BigWorld


class QuestsGetter:
	def __init__(self):
		self.callback_complete = False
		self.callback_result = None
		
	def get_quests_data(self, databaseID):
		"""
		Queries the database for quest data using BigWorld.executeRawDatabaseCommand().
		"""
		raise DeprecationWarning("QuestsGetter.get_quests_data :: This method is deprecated.")
		command = "SELECT tokens, potapovQuests, quests FROM quests_db WHERE dbid = %s" % databaseID
		
		def callback(result, numRows, error):
			if error:
				raise ValueError("QuestsGetter.get_quests_data :: Error occurred while fetching quests data: %s" % error)
			return result
		
		BigWorld.executeRawDatabaseCommand(command, callback)
		
	def get_quests_data_keyed(self, databaseID, key=None):
		"""
		Queries the database for quest data using BigWorld.executeRawDatabaseCommand() and returns the data keyed by the specified key.
		"""
		raise DeprecationWarning("QuestsGetter.get_quests_data_keyed :: This method is deprecated.")
		if key is None: raise ValueError("QuestsGetter.get_quests_data_keyed :: requires a key argument.")
		
		command = "SELECT %s FROM quests_db WHERE dbid = %s" % key, databaseID
		
		def callback(result, numRows, error):
			if error:
				raise ValueError("QuestsGetter.get_quests_data_keyed :: Error occurred while fetching quests data: %s" % error)
			return result
		
		BigWorld.executeRawDatabaseCommand(command, callback)
