import BigWorld
from bwdebug import *
# import GarbageCollectionDebug
# import HierarchyCheck
import os
import Watchers

# from SpaceData import SPACE_DATA_GEOMETRY_LOADED

# from cPickle import loads
# from SpaceLoader import SPACE_DATA_SPACE_LOADER

try:
	# srvtest is optional
	# It will only be used if we run Fantasydemo from the testing environment
	import srvtest
except ImportError:
	pass


DO_GC_DUMP = False
gFirstSpaceID = 0
gSpaceIDHook = None

def onSpaceData(spaceID, entryID, key, value):
	print "onSpaceData: spaceID", spaceID, \
	 "entryID", entryID, "key", key, "value", len(value)
	
	print "[bwtest] onSpaceData: ", spaceID, key
	#if 0 <= key and key <= 255:
	#	return
	
	global gFirstSpaceID
	global gSpaceIDHook
	
	gFirstSpaceID = spaceID
	if gSpaceIDHook is not None:
		print "[bwtest] onSpaceData: called the hook! "
		gSpaceIDHook( spaceID )


def onSpaceDataDeleted(spaceID, deletedEntryID, key, deletedValue):
	""" Callback function when space data was deleted. """
	for i, e in BigWorld.entities.items():
		if e.isReal() and \
				hasattr( e, 'onSpaceDataDeleted' ) and \
				e.spaceID == spaceID:
				e.onSpaceDataDeleted( spaceID, deletedEntryID,
						key, deletedValue )


def onInit(isReload):
	""" Callback function when scripts are loaded. """

	# Check that the entitydef inheritance hierarchy strictly
	# matches the Python class hierarchy.

	# Load all the runscript watchers for this cellapp
	# Watchers.addWatchers()

	# HierarchyCheck.checkTypes()
	pass


def onFini():

	# Need to name file so that it doesn't overwrite base's log
	# There can be multiple cellapps running so name by PID as well
	# pid = os.getpid()
	# hostname = os.uname()[ 1 ]
	# numLeaks = GarbageCollectionDebug.gcDump(
	# 	DO_GC_DUMP, "gcDump.cell.%s.%d.log" % ( hostname, pid ) )
	#
	# if numLeaks > 0:
	# 	DEBUG_MSG( "Potential circular references" )
	# 	DEBUG_MSG( "Number of leaks:", numLeaks )
	pass


def onAllSpaceGeometryLoaded( spaceID, isBootstrap, mapping ):
	# for i, e in BigWorld.entities.items():
	# 	if e.isReal() and \
	# 			hasattr( e, 'onAllSpaceGeometryLoaded' ) and \
	# 			e.spaceID == spaceID:
	# 		e.onAllSpaceGeometryLoaded( spaceID, isBootstrap, mapping )
	#
	# BigWorld.setSpaceData( spaceID, SPACE_DATA_GEOMETRY_LOADED, "" )
	#
	# INFO_MSG( "%s in space %d at game time %s" % \
	#    (mapping, spaceID, str( BigWorld.time() )) )
	pass


def hasLoadedAllGeometry( spaceID ):
	# try:
	# 	BigWorld.getSpaceDataFirstForKey( spaceID, SPACE_DATA_GEOMETRY_LOADED )
	# 	return True
	# except:
	# 	return False
	pass

# Cell bootstrap script

def onCellAppReady( isFromDB ):
	pass

def hookOnSpaceID( callback ):
	global gSpaceIDHook
	gSpaceIDHook = callback


def getSpaceID():
	global gFirstSpaceID
	return gFirstSpaceID

# BWPersonality.py

import Watchers

# wot.py
