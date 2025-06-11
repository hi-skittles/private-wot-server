# Import standard modules
import sys
import os
import time
import threading
import operator
import itertools
import logging

# Import third party modules
import cherrypy

# Import stuff from stat_logger
import bwsetup
bwsetup.addPath("../../stat_logger")
bwsetup.addPath("../../stat_logger/model")
import dbmanager
import prefclasses
import constants
import prefxml


# Make log object
log = logging.getLogger( "stat_grapher.md" )

# A global pref tree manager, which stores
# a single preference object per database log.
# Preftrees can be shared across threads safely because
# it doesn't get written to.
ptManager = None

# List of collection preferences
class PrefTreeManager:

	class PrefTreeRecord:
		def __init__( self, prefTree, time ):
			self.prefTree = prefTree
			self.time = time

	# Remove after 60 seconds of inactivity
	timeout = 5
	prefTreeLock = threading.Lock()

	def __init__( self ):
		self.ptRecords = {}


	def addPrefTree( self, name, prefTree ):
		self.prefTreeLock.acquire()
		self.ptRecords[name] = self.PrefTreeRecord( prefTree, time.time() )
		self.prefTreeLock.release()

	def touchPrefTree( self, name ):
		self.ptRecords[name].time = time.time()
		#print "Touching pref tree %s" % name

	def cleanExpiredPrefTrees( self ):
		now = time.time()
		cutoff = time.time() - self.timeout
		todelete = []
		for name, record in self.ptRecords.iteritems():
			if record.time < cutoff:
				todelete.append( name )

		self.prefTreeLock.acquire()
		for name in todelete:
			del self.ptRecords[name]
			print "Cleaning unused preftree for %s" % name
		self.prefTreeLock.release()

	def getPrefTree( self, name ):
		self.prefTreeLock.acquire()
		pt = self.ptRecords[name].prefTree
		self.prefTreeLock.release()
		return pt

	def connected( self, name ):
		return self.ptRecords.has_key( name )

	def requestDbManager( self, name ):
		ct = threading.currentThread()
		#print "Current thread: %s" % (ct.getName())
		#print dir(cherrypy.thread_data), id(cherrypy.thread_data)
		#print "Requesting from thread %d!" % cherrypy.thread_data.threadID

		funcStart = time.time()
		log.debug( "requestDbManager: log = %s", name )

		if not self.connected( name ):
			log.debug( "  requestDbManager: Not connected to %s!", name )
			connectStart = time.time()
			cherrypy.thread_data.db.connectToLogDb( name )
			prefStart = time.time()
			log.debug( "  requestDbManager: Connecting took %s",
				prefStart - connectStart )
			prefTree = cherrypy.thread_data.db.getLogDbPrefTree()
			log.debug( "  requestDbManager: Getting preftree took %.3fs",
				time.time() - prefStart )
			self.addPrefTree( name, prefTree )
		else:
			switchStart = time.time()
			cherrypy.thread_data.db.switchToLogDb( name )
			prefStart = time.time()
			log.debug( "  requestDbManager: Switching took %.3fs",
				prefStart - switchStart )
			prefTree = self.getPrefTree( name )
			log.debug( "  requestDbManager: Getting preftree took %.3fs",
				time.time() - prefStart )
			self.touchPrefTree( name )
		self.cleanExpiredPrefTrees()

		log.debug( "requestDbManager: Took %.3fs", time.time() - funcStart )
		return cherrypy.thread_data.db, prefTree

# This just returns the db manager which is potentially not
# connected to a specific database
def getRawDbManager( ):
	return cherrypy.thread_data.db

def setup( prefFilePath, options ):
	global ptManager

	# { threadID -> { dbName -> LogDbConn} }
	def setThreadId( threadID ):
		cherrypy.thread_data.threadID = threadID
		log.debug( "Setting thread id to %d" % ( threadID ) )

	def createDbManager( threadID ):
		threadDbManager = dbmanager.DbManager( options.dbStoreConfig )
		threadDbManager.setPrefFilePath( prefFilePath )

		cherrypy.thread_data.db = threadDbManager 
		log.debug( "Creating db manager for thread %d" % (threadID) )

	cherrypy.server.on_start_thread_list.extend(
		[setThreadId, createDbManager] )

	ptManager = PrefTreeManager()
