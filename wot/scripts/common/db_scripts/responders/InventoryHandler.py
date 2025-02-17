from twisted.internet import defer
from bwdebug import TRACE_MSG
import db_scripts.DatabaseHandler as DBHandler


def get_inventory(normalizedName, columns, callback):
	TRACE_MSG('InventoryHandler : get_inventory :: normalizedName=%s' % normalizedName)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.GetInventoryData(normalizedName, callback, columns)
	DBHandler.add_task(task)
	return deferred

def set_inventory(normalizedName, data, columns, callback):
	TRACE_MSG('InventoryHandler : set_inventory :: normalizedName=%s' % normalizedName)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.SetInventoryData(normalizedName, data, callback, columns)
	DBHandler.add_task(task)
	return deferred
