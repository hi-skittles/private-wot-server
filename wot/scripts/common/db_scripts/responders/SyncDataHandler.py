from twisted.internet import defer
from bwdebug import TRACE_MSG
import db_scripts.DatabaseHandler as DBHandler


def get_sync_data(normalizedName, databaseID, callback):
	TRACE_MSG('SyncDataHandler : get_sync_data :: databaseID=%s' % normalizedName)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.GetFullSyncData(normalizedName, databaseID, callback)
	DBHandler.add_task(task)
	return deferred
