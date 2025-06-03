from twisted.internet import defer
from bwdebug import TRACE_MSG
import db_scripts.DatabaseHandler as DBHandler


def get_stats(normalizedName, columns, callback):
	TRACE_MSG('StatsHandler : get_stats :: normalizedName=%s' % normalizedName)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.GetStatsData(normalizedName, callback, columns)
	DBHandler.add_task(task)
	return deferred

def update_stats(normalizedName, data, columns, callback):
	TRACE_MSG('StatsHandler : set_stats :: normalizedName=%s' % normalizedName)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.SetStatsData(normalizedName, data, callback, columns)
	DBHandler.add_task(task)
	return deferred