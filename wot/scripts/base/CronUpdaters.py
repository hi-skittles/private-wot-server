import cPickle
import pprint
import os
import sched, time

import BigWorld

import ResMgr

import BackgroundTask
from bwdebug import TRACE_MSG, DEBUG_MSG

threadManager = None

def init():
	global threadManager
	if threadManager is None:
		threadManager = BackgroundTask.Manager("Schedulers")
		threadManager.startThreads(1)
		TRACE_MSG('Schedulers :: Initialized background thread manager.')
	return True

def fini():
	global threadManager
	if threadManager is not None:
		threadManager.stopAll()
		threadManager = None
		TRACE_MSG('Schedulers :: Stopped background thread manager.')

def add_task(task):
	if threadManager is None:
		assert threadManager is None, "Schedulers :: Background thread manager is not initialized. Has it been initialized in the personality script?"
		raise RuntimeError("UniversalBackgroundDatabaseHandler is not initialized.")
	threadManager.addBackgroundTask(task)


class RemoveExpiredPremium(BackgroundTask.BackgroundTask):
	"""
	Removes premium attr flag from expired premium accounts.
	"""
	
	def __init__(self, callback):
		self.databaseID = None
		self.callback = callback
		self.result = None
		self.filepath = None
	
	def doBackgroundTask(self, bgTaskMgr, threadData):
		TRACE_MSG('RemoveExpiredPremium (background) :: databaseID=%s' % self.databaseID)
		self.filepath = ResMgr.resolveToAbsolutePath('server/database_files/quests/')
		if not os.path.exists(self.filepath):
			os.makedirs(self.filepath)
		filename = os.path.join(self.filepath, "%s" % self.databaseID)  # bit weedy, innit
		if not os.path.isfile(filename):
			self.result = self.__initEmptyQuests()  # dict
			
			try:
				with open(filename, 'wb') as file:
					pprint.pprint(self.result, stream=file)
			except Exception as e:
				raise Exception("RemoveExpiredPremium :: Error occurred while writing inventory data (init)=%s" % e)
		else:
			try:
				with open(filename, 'rb') as file:
					self.result = file.read()  # str
				self.result = eval(self.result)  # dict
			except Exception as e:
				raise Exception("RemoveExpiredPremium :: Error occurred while fetching inventory data=%s" % e)
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		TRACE_MSG('RemoveExpiredPremium (foreground) :: databaseID=%s' % self.databaseID)
		self.callback(self.result)