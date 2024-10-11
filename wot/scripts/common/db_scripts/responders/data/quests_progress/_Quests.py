import ast
import sqlite3

import BigWorld
import ResMgr
from bwdebug import TRACE_MSG


class _Quests:
    def __init__(self):
        pass
    
    def build_quests_for_client(self, tokens, potapovQuests, quests):
        """
        Builds quests data for the client.

        Args:
            potapovQuests (str): The potapov quests data as a string.
            quests (str): The quests data as a string.
            tokens (str): The tokens data as a string.

        Returns:
            dict: A dictionary containing the quests data for the client.
        """
        rdata = {"potapovQuests": ast.literal_eval(potapovQuests), "quests": ast.literal_eval(quests),
                 "tokens": ast.literal_eval(tokens)}
        return rdata

    def init_empty_quests(self, databaseID):
        """
        Initializes empty quests data for a specific database ID.

        Args:
            databaseID (int): The ID of the database to initialize quests data for.

        Returns:
            dict: A dictionary containing the initialized quests data.
        """
        raise DeprecationWarning("This method is deprecated. Use QuestsHandler.requestQuestsForClient instead.")
        dbdir = ResMgr.resolveToAbsolutePath('scripts/db/quests/quests_db.sqlite')
        connection = sqlite3.connect(dbdir)
        cursor = connection.cursor()
        
        tokens = '{\"count\": 0, \"expiryTime\": 0}'
        potapovQuests = '{\"compDescr\": \"\", \"slots\": 0, \"selected\": [], \"rewards\": {}, \"unlocked\": {}}'
        quests = '{\"progress\": 0}'
        
        command = "INSERT INTO quests_db (dbid, tokens, potapovQuests, quests) VALUES('{}', '{}', '{}', '{}');".format(databaseID, tokens, potapovQuests, quests)
        cursor.execute(command)
        connection.commit()
        connection.close()
		
        return self.build_quests_for_client(potapovQuests, quests, tokens)