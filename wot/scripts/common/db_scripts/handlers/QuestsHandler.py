from twisted.internet import defer
from bwdebug import TRACE_MSG
import db_scripts.DatabaseHandler as DBHandler


def get_quests(normalizedName, columns, callback):
	TRACE_MSG('QuestsHandler : get_quests :: normalizedName=%s' % normalizedName)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.GetQuestsData(normalizedName, callback, columns)
	DBHandler.add_task(task)
	return deferred
