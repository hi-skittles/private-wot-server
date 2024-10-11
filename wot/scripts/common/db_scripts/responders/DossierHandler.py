import ast
from twisted.internet import defer

import BigWorld
from bwdebug import TRACE_MSG, DEBUG_MSG
import logging

import db_scripts.DatabaseHandler as DBHandler


def get_dossiers(databaseID, callback):
	TRACE_MSG('DossierHandler : get_dossiers :: databaseID=%s' % databaseID)
	deferred = defer.Deferred()
	deferred.addCallback(callback)
	task = DBHandler.GetDossierData(databaseID, callback)
	DBHandler.add_task(task)
	return deferred

def set_dossiers(databaseID, data, callback):
	raise NotImplemented
