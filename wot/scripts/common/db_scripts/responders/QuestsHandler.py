from twisted.internet import defer
from bwdebug import TRACE_MSG, DEBUG_MSG
import db_scripts.DatabaseHandler as DBHandler


def get_quests(normalizedName, callback, *columns):
	TRACE_MSG('QuestsHandler : get_quests :: databaseID=%s' % normalizedName)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.GetQuestsData(normalizedName, callback, *columns)
	DBHandler.add_task(task)
	return deferred
