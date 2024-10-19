import logging
import BigWorld

import items
from bwdebug import *
import os
import ResMgr
import GarbageCollectionDebug
import HierarchyCheck

# This is imported here to avoid loading in the main thread.
# import UserDataObjectRef

import gc
import pprint

from db_scripts import DatabaseHandler
import CronUpdaters

DO_GC_DUMP = False

try:
	# srvtest is optional
	# It will only be used if we run Fantasydemo from the testing environment
	import srvtest
except ImportError:
	pass

# ------------------------------------------------------------------------------
# Section: Callbacks
# ------------------------------------------------------------------------------
def onInit(isReload):
	""" Callback function when scripts are loaded. """

	# Check that the entitydef inheritance hierarchy strictly
	# matches the Python class hierarchy.

	HierarchyCheck.checkTypes()
	WARNING_MSG("wot.base.onInit: isReload={}".format(str(isReload)))
	DatabaseHandler.init()
	# CronUpdaters.init()
	
	items.init(True, {})

def onFini():
	WARNING_MSG("wot.base.onFini")
	# Need to name file so that it doesn't overwrite the cell's log
	# There can be multiple cellapps running so name by PID as well
	pid = os.getpid()
	hostname = os.uname()[1]
	numLeaks = GarbageCollectionDebug.gcDump(DO_GC_DUMP,
		"gcDump.base.%s.%d.log" % (hostname, pid))

	if numLeaks > 0:
		DEBUG_MSG("FantasyDemo.onFini: Potential circular references")
		DEBUG_MSG("Number of leaks:", numLeaks)

	# We also run fini here in case it isn't a controlled shutdown. This helps
	# avoid the BaseApp failing to shut down cleanly due to a race condition
	# with thread startup and shutdown. We still perform regular shutdown in
	# onAppShutDown as that allows the NoteDataStore subsystem to cleanly
	# terminate.
	DatabaseHandler.fini()
	# CronUpdaters.fini()

def onAppReady(isBootstrap, didAutoLoadEntitiesFromDB):
	# Load all the runscript watchers for this baseapp
	DEBUG_MSG("wot.base.onAppReady isBootstrap: {}".format(str(isBootstrap)))

def onAppShutDown(state):
	WARNING_MSG("wot.base.onAppShutDown: state={}".format(str(state)))
	if state == 0:
		DatabaseHandler.fini()
		# CronUpdaters.fini()

def onCellAppDeath(addr):
	WARNING_MSG("wot.base.onCellAppDeath: addr={}".format(str(addr)))
	pass
	
def onBaseAppData(key, value):
	TRACE_MSG("wot.base.onBaseAppData: key={}, value={}".format(key, value))

# ------------------------------------------------------------------------------
# Section: Common base class
# ------------------------------------------------------------------------------
class Base(BigWorld.Base):
	def __init__(self):
		DEBUG_MSG("Base.__init__")
		BigWorld.Base.__init__( self )

		# This is useful if using disaster recovery.
		if not self.databaseID:
			self.writeToDB()

		if hasattr( self, "cellData" ):
			try:
				cell = self.createOnCell
				self.createOnCell = None
			except AttributeError, e:
				cell = None

			if cell != None:
				self.createCellEntity( cell )
			elif self.cellData["spaceID"]:
				self.createCellEntity()

	def onSpaceLoaderDestroyed(self):
		"""
		The SpaceLoader that created us has been destroyed, which means
		our source geometry is being unloaded.
		"""
		WARNING_MSG("Base.onSpaceLoaderDestroyed")
		self.respawnInterval = 0
		if self.hasCell:
			self.destroyCellEntity()
		else:
			self.destroy()

	def onLoseCell(self):
		WARNING_MSG("Base.onLoseCell")
		rsm = None
		if hasattr( self, 'respawnInterval' ) and self.respawnInterval != 0:
			gb = BigWorld.globalBases
			if not gb.has_key( 'RespawnManager' ):
				rsm = BigWorld.createEntity( 'RespawnManager' )
			else:
				rsm = gb['RespawnManager']
			rsm.registerForRespawn( self.__module__, self.entityData, self.respawnInterval )
		self.destroy()

# At the bottom to avoid circular import issue
import Watchers