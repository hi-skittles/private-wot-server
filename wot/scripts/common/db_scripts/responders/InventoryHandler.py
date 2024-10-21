import ast
from twisted.internet import defer

import BigWorld
from bwdebug import TRACE_MSG, DEBUG_MSG
import logging

import db_scripts.DatabaseHandler as DBHandler


def get_inventory(databaseID, callback):
	TRACE_MSG('InventoryHandler : get_inventory :: databaseID=%s' % databaseID)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.GetInventoryData(databaseID, callback)
	DBHandler.add_task(task)
	return deferred

def set_inventory(databaseID, data, callback):
	TRACE_MSG('InventoryHandler : set_inventory :: databaseID=%s' % databaseID)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.SetInventoryData(databaseID, data, callback)
	DBHandler.add_task(task)
	return deferred
