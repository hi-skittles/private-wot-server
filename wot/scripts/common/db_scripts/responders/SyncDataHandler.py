from twisted.internet import defer

from bwdebug import TRACE_MSG, DEBUG_MSG

import db_scripts.DatabaseHandler as DBHandler


def get_sync_data(databaseID, callback):
    TRACE_MSG('SyncDataHandler : get_sync_data :: databaseID=%s' % databaseID)
    deferred = defer.Deferred()
    deferred.addCallback(callback)
    task = DBHandler.GetFullSyncData(databaseID, callback)
    DBHandler.add_task(task)
    return deferred