import ast
from twisted.internet import defer

import BigWorld
from bwdebug import TRACE_MSG, DEBUG_MSG
import logging

import db_scripts.DatabaseHandler as DBHandler


def get_quests(databaseID, callback):
    TRACE_MSG('QuestsHandler : get_quests :: databaseID=%s' % databaseID)
    deferred = defer.Deferred()
    deferred.addCallback(callback)
    task = DBHandler.GetQuestsData(databaseID, callback)
    DBHandler.add_task(task)
    return deferred

def updateQuests(databaseID, key=None, value=None):
    raise DeprecationWarning('QuestsHandler :: updateQuests :: This method is deprecated and should not be used.')
    TRACE_MSG('QuestsHandler :: updateQuests :: databaseID=%s, key=%s, value=%s' % (databaseID, key, value))
    self.updater.update_quests_data(databaseID=databaseID, key=key, value=value)