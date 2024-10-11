import ast
from twisted.internet import defer

import BigWorld

from adisp import async, process
from bwdebug import TRACE_MSG, DEBUG_MSG
import logging

import db_scripts.DatabaseHandler as DBHandler


def get_stats(databaseID, callback):
	TRACE_MSG('StatsHandler : get_stats :: databaseID=%s' % databaseID)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.GetStatsData(databaseID, callback)
	DBHandler.add_task(task)
	return deferred

def update_stats(databaseID, data, callback):
	TRACE_MSG('StatsHandler : set_stats :: databaseID=%s' % databaseID)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.SetStatsData(databaseID, data, callback)
	DBHandler.add_task(task)
	return deferred