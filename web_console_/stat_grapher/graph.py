"""
TurboGears controller for retrieving statistics from
StatLogger database and serving it to Flash based StatGrapher clients.
"""

# Import standard python libraries
import time
import sys
import os
import traceback
import logging
import random
import socket

# Import third party libraries
import turbogears, turbogears.config
import cherrypy
import amfgateway
import sqlobject

# Import local modules
import managedb
import model
import graphutils
import utils
import graphprefs

# Import common SQLObject modules
from web_console.common import util

# Import our modules
import constants
from pycommon import cluster


# Logger objects
sqlLog = logging.getLogger( "stat_grapher.sql" )
apiLog = logging.getLogger( "stat_grapher.api" )
amfLog = logging.getLogger( "stat_grapher.amf" )

class StatGrapherBackend( amfgateway.AMFGateway ):
	"""
	Controller for StatGrapher, and also serves as its backend.
	"""

	def __init__( self ):
		amfgateway.AMFGateway.__init__( self, "StatGrapherBackend" )
		self.machineRequester = MachineRequester( self )
		self.processRequester = ProcessRequester( self )
		self.prefsRequester = graphprefs.PrefRequester( self )

		self.cluster = cluster.cache.get()
		self.userDisplayPrefs = {}

	# -------------------------------------------------------------------------
	# Section: Exposed TurboGears Methods
	# -------------------------------------------------------------------------
	@turbogears.expose( template="stat_grapher.templates.graphview" )
	def processes( self, logDb, user, desiredPointsPerView=80,
			minGraphWidth=250, minGraphHeight=200, debug=False ):
		"""
		Make the process view for a particular user and log database.
		"""
		return dict(
			log = logDb,
			user = user,
			serviceURL = "/statg/graph/amfgateway",
			profile = "process",
			desiredPointsPerView = desiredPointsPerView,
			minGraphWidth = minGraphWidth,
			minGraphHeight = minGraphHeight,
			debug = debug
		)

	@turbogears.expose( template="stat_grapher.templates.graphview" )
	def machines( self, logDb, desiredPointsPerView=80,
			minGraphWidth=250, minGraphHeight=200, debug=False ):
		"""
		Make the machine view for a particular log database.
		"""
		apiLog.info( "machines, logDb = %s", logDb )
		return dict(
			log = logDb,
			user = None,
			serviceURL = "/statg/graph/amfgateway",
			profile = "machine",
			desiredPointsPerView = desiredPointsPerView,
			minGraphWidth = minGraphWidth,
			minGraphHeight = minGraphHeight,
			debug = debug
		)

	# -------------------------------------------------------------------------
	# Section: Exposed AMF Gateway Methods
	# -------------------------------------------------------------------------
	#@utils.logFunc( apiLog.info )
	@amfgateway.expose
	def requestPrefTree( self, logDb ):
		dbManager, prefTree = managedb.ptManager.requestDbManager( logDb )
		tickInterval = dbManager.getLogDbInterval()
		prefTree.tickInterval = tickInterval
		return prefTree

	@amfgateway.expose
	def requestProcessInfo( self, *args, **kwargs ):
		return self.processRequester.requestProcessInfo( *args, **kwargs )

	@amfgateway.expose
	def requestMachineInfo( self, *args, **kwargs ):
		return self.machineRequester.requestMachineInfo( *args, **kwargs )

	@amfgateway.expose
	def requestMachineStatistics( self, logDb, ips, fromTick, toTick,
		resolution ):
		"""
		Retrieve machine statistics from the server
		"""
		sessionUser = util.getSessionUser()
		displayPrefs = self.prefsRequester.retrieveDisplayPrefs( logDb,
			sessionUser )
		dbManager, prefTree = managedb.ptManager.requestDbManager( logDb )
		enabledStats = displayPrefs["enabledMachineStatOrder"]
		statList = [prefTree.machineStatPrefById( int(id) ) \
			for id in enabledStats]
		if ips != None:
			ips = [utils.inet_aton( ip ) for ip in ips]
		window = prefTree.windowPrefs[ int(resolution) ]
		result = self.machineRequester.retrieveStatistics( logDb, None,
			"machine", statList, ips, window, fromTick, toTick )
		#apiLog.debug( "Machine stats: %s", result )
		return result

	@amfgateway.expose
	def requestMachineStatisticsByTime( self, logDb, ips, fromTime, toTime,
		resolution ):
		"""
		Retrieve machine statistics from the server
		"""
		dbManager, prefTree = managedb.ptManager.requestDbManager( logDb )
		cursor = dbManager.getLogDbCursor()
		fromTick, toTick = DatabaseRequester.getTickRange( cursor, fromTime,
			toTime  )
		cursor.close()
		return self.requestMachineStatistics( logDb, ips, fromTick, toTick,
			resolution )

	@amfgateway.expose
	def requestProcessStatistics( self, logDb, uid, procType, dbIDs,
			fromTick, toTick, resolution ):
		"""
		Retrieve process statistics from the server
		"""

		utils.logArgs( apiLog.debug )

		sessionUser = util.getSessionUser()
		displayPrefs = self.prefsRequester.retrieveDisplayPrefs( logDb,
			sessionUser )
		dbManager, prefTree = managedb.ptManager.requestDbManager( logDb )
		enabledStats = displayPrefs["enabledProcStatOrder"][procType]
		statList = [prefTree.procPrefs[procType].statPrefById( int(id) ) \
			for id in enabledStats]
		if dbIDs != None:
			dbIDs = [int( dbId ) for dbId in dbIDs ]
		window = prefTree.windowPrefs[ int(resolution) ]
		return self.processRequester.retrieveStatistics( logDb, uid,
			procType, statList, dbIDs, window, fromTick, toTick )

	@amfgateway.expose
	def requestProcessStatisticsByTime( self, logDb, uid, procType, dbIDs,
			fromTime, toTime, resolution ):
		"""
		Retrieve process statistics from the server
		"""
		dbManager, prefTree = managedb.ptManager.requestDbManager( logDb )
		cursor = dbManager.getLogDbCursor()
		fromTick, toTick = DatabaseRequester.getTickRange( cursor, fromTime,
			toTime  )
		cursor.close()
		return self.requestProcessStatistics( logDb, uid, procType, dbIDs,
			fromTick, toTick, resolution )


	@amfgateway.expose
	@utils.logFunc( apiLog.info )
	def requestDisplayPrefs( self, logDb ):
		"""
		Request the user's display preference for this log. Note that
		the current session is used to determine the user.
		"""
		user = util.getSessionUser()
		result = self.prefsRequester.retrieveDisplayPrefs( logDb, user )
		#apiLog.debug( "requestDisplayPrefs: Result is %s", result )
		return result

	@amfgateway.expose
	@utils.logFunc( apiLog.info )
	def requestLogRange( self, logDb ):
		"""Returns the start and end times of the log"""
		dbManager, prefTree = managedb.ptManager.requestDbManager( logDb )
		cursor = dbManager.getLogDbCursor()

		query = """ SELECT id, time FROM %s ORDER BY id ASC LIMIT 1 """ \
			% (constants.tblStdTickTimes)
		utils.timeQuery( sqlLog.info, "requestLogRange(Start)", cursor, query )
		startTick, startTime = cursor.fetchone()

		# Grab the second last tick, as the last tick usually contains
		# incomplete stats in a live database
		query = """ SELECT id, time FROM %s ORDER BY id DESC LIMIT 1,1 """ \
			% (constants.tblStdTickTimes)
		utils.timeQuery( sqlLog.info, "requestLogRange(End)", cursor, query )
		endTick, endTime = cursor.fetchone()

		apiLog.info( "requestLogRange: startTime: %s, endTime: %s", startTime, endTime )

		return {"start": startTime, "end": endTime}


	@amfgateway.expose
	def setMachineStatColour( self, logDb, prefId, newColour ):
		"""
		Changes a colour of a machine statistic. (per-user)
		"""
		user = util.getSessionUser()
		self.prefsRequester.setMachineStatColour( logDb, user, prefId, newColour )

	@amfgateway.expose
	def setProcessStatColour( self, logDb, procType, prefId, newColour ):
		"""
		Changes a colour of a process statistic. (per-user)
		"""
		user = util.getSessionUser()
		self.prefsRequester.setProcessStatColour( logDb, user, procType,
			prefId, newColour )

	@amfgateway.expose
	def saveEnabledProcStatOrder( self, logDb, procType, statList ):
		"""
		Save the process statistics order list for the given log and process
		type.
		"""
		user = util.getSessionUser()
		self.prefsRequester.saveEnabledProcStatOrder( logDb, user, procType,
			statList )

	@amfgateway.expose
	def saveEnabledMachineStatOrder( self, logDb, statList ):
		"""
		Save the machine statistics order list for the given log
		"""
		user = util.getSessionUser()
		self.prefsRequester.saveEnabledMachineStatOrder( logDb, user, statList )

# -------------------------------------------------------------------------
# Section: DatabaseRequester
# -------------------------------------------------------------------------
class DatabaseRequester:

	def __init__( self ):
		self.idColumn = None
		self.seenObjTableName = None
		self.seenObjIdColumn = None

	def getTableName( self, type ):
		raise Exception( "Abstract function, please implement in a subclass!" )

	# -------------------------------------------------------------------------
	# Section: Utility methods
	# -------------------------------------------------------------------------
	@staticmethod
	@utils.logFunc( apiLog.debug )
	def getTickRange( cursor, fromTime, toTime ):
		"""
		Given a start time and end time, return the ticks corresponding
		to that time range.

		Returns (fromTick, toTick).
		"""
		#utils.logArgs( apiLog.debug )

		fromTime = int( fromTime )
		toTime = int( toTime )

		query = "SELECT tick1.id FROM %s tick1 WHERE tick1.time = " \
			"  (SELECT MAX(tick2.time) FROM %s tick2 " \
			"  WHERE tick2.time < %d)" \
			% (constants.tblStdTickTimes, constants.tblStdTickTimes, fromTime)

		utils.timeQuery( sqlLog.info, "getTickRange(max)", cursor, query )
		row = cursor.fetchone()
		if row: fromTick = row[0]
		else: fromTick = None

		query = "SELECT tick1.id FROM %s tick1 WHERE tick1.time = " \
			"  (SELECT MIN(tick2.time) FROM %s tick2 " \
			"  WHERE tick2.time > %d)" \
			% (constants.tblStdTickTimes, constants.tblStdTickTimes, toTime)

		utils.timeQuery( sqlLog.info, "getTickRange(min)", cursor, query )
		row = cursor.fetchone()
		if row: toTick = row[0]
		else: toTick = None

		apiLog.debug( "getTickRange: Returning values (%s, %s)",
			fromTick, toTick )
		return fromTick, toTick

	@staticmethod
	def chooseResolution( windowPrefs, tickInterval, startTime, endTime ):
		"""Given a start and end time, determine
		the best log resolution to use for querying."""
		wantedWindow = windowPrefs[0]
		for window in windowPrefs:
			windowStart = (endTime - \
				(window.samples * window.samplePeriodTicks) * \
				tickInterval) * 1000
			if windowStart < startTime:
				wantedWindow = window
				break
		return wantedWindow

	@staticmethod
	@utils.logFunc( apiLog.debug )
	def transformRows( statPrefs, rows ):
		"""
		Given a result from rows, convert into a dictionary format
		which is more palatable for use in flash.

		Row format: [tick,time,count,rest of stats]
		"""
		statDict = {}

		statDict["times"] = []
		statDict["ticks"] = []
		statDict["num"] = []
		statDict["data"] = {}
		for statPref in statPrefs:
			statDict["data"][str(statPref.dbId)] = []

		for row in rows:
			statDict["ticks"].append( row[0] )
			statDict["times"].append( row[1] )
			statDict["num"].append( row[2] )
			for i in range( len( statPrefs) ):
				statDict["data"][str(statPrefs[i].dbId)].append( row[3 + i] )

		return statDict

	# -------------------------------------------------------------------------
	# Section: Statistic retrieval method
	# -------------------------------------------------------------------------
	@utils.logFunc( apiLog.info )
	def retrieveStatistics( self, logDb, uid, objType, statPrefs,
			dbIDs, window, fromPoint, toPoint ):
		"""
		Get process statistic data for a process type and at a window in a time
		range.

		@param logDb:		The log database name
		@param uid:			The server user ID
		@param objType:		The type of the object (e.g. "CellApp", "Machine")
		@param statPrefs:	A list of StatPref objects which we'll use to
							construct the query
		@param dbIDs:		A list of the process database IDs, or None for all
							processes of the given process type
		@param window:		The window aggregation preference
		@param fromTick:	The start tick. If fromTick is 0 and toTick is None,
							then all available data on this aggregation window
							is retrieved.
		@param toTick:		The end tick. If both fromTick and toTick are both
							None, then empty data is returned.
							Whether to include the tick time as well. This is
							useful in skeleton data.
		"""

		utils.logArgs( apiLog.info, name="retrieveStatistics(%s)" % (objType) )

		dbManager, prefTree = managedb.ptManager.requestDbManager( logDb )
		cursor = dbManager.getLogDbCursor()
		tickInterval = dbManager.getLogDbInterval()

		# Name of table containing stats (e.g. "stat_cellapp")
		tableName = self.getTableName( prefTree, objType )
		idColumn = self.idColumn                  # e.g. "process" or "machine"
		seenObjTableName = self.seenObjTableName  # e.g. "seen_processes"
		seenObjIdColumn = self.seenObjIdColumn    # e.g. "ip" or "id"

		# Force userid to int
		if uid != None: uid = int( uid )
		if fromPoint != None: fromPoint = int( fromPoint )
		if toPoint != None: toPoint = int( toPoint )

		# Convert dbIDs back to integers
		queryMultipleItems = (not dbIDs or len(dbIDs) > 1)

		# Build the column names
		columns = [ 'stat.tick', 'tick.time AS tickTime' ]

		if queryMultipleItems:
			columns.append( "COUNT(stat.%s)" % (idColumn) )
		else:
			columns.append( "1" )

		# If we're smashing multiple processes together, add
		# the consolidation function e.g. "MAX(mem)" instead of
		# just "mem".
		for statPref in statPrefs:
			if queryMultipleItems:
				columns.append( statPref.consolidateColumn( "stat" ) )
			else:
				columns.append( "stat.%s" % statPref.columnName )

		queryTableName = "%s_lvl_%03d" % (tableName, window.dbId)

		query = "SELECT %s FROM %s stat " % \
			(", ".join( columns ), queryTableName)
		query += "JOIN %s tick ON stat.tick = tick.id " % \
			(constants.tblStdTickTimes,)

		# "obj" is either tblSeenProcesses or tblSeenMachines
		query += "JOIN %s seenObj ON stat.%s = seenObj.%s " \
			% (seenObjTableName, idColumn, seenObjIdColumn)

		# Restrict stats to one user (make sure this does not
		# happen in a machine query, as the machine table does
		# not have a userid column
		if uid != None:
			query += "WHERE seenObj.userid = %d " % (uid )

		if dbIDs:
			query += "AND seenObj.%s IN (%s) " % \
				(seenObjIdColumn, ", ".join( str(dbID) for dbID in dbIDs ))

		# Restrict stats to a time range
		extendAmount = window.samplePeriodTicks

		if fromPoint and fromPoint > 0:
			fromPoint -= extendAmount
			query += "AND tick.id > %d " % (fromPoint,)
		if toPoint:
			toPoint += extendAmount
			query += "AND tick.id < %d " % (toPoint,)

		# Group by if we're consolidating multiple items together
		if queryMultipleItems:
			query += "GROUP BY stat.tick "

		# Order stats
		query += "ORDER BY stat.tick"

		utils.timeQuery( sqlLog.info, "retrieveStatistics", cursor, query,
			printSQL=True )
		rows = cursor.fetchall()
		cursor.close()
		stats = self.transformRows( statPrefs, rows )

		return stats

# -------------------------------------------------------------------------
# Section: MachineRequester
# -------------------------------------------------------------------------
class MachineRequester( DatabaseRequester ):
	def __init__( self, backend ):
		self.backend = backend
		self.label = "Machine"
		self.idColumn = "machine"
		self.seenObjTableName = constants.tblSeenMachines
		self.seenObjIdColumn = "ip"

	def getTableName( self, prefTree, type ):
		return constants.tblStatMachines

	@utils.logFunc( apiLog.info, name="requestMachineInfo" )
	def requestMachineInfo( self, logDb, startTime, endTime, ips = None ):
		"""
		Request details about machines.
		"""
		dbManager, prefTree = managedb.ptManager.requestDbManager( logDb )
		cursor = dbManager.getLogDbCursor()

		utils.logArgs( apiLog.debug )

		# Step 1: Get the tick range for the new time range
		fromTick, toTick = self.getTickRange( cursor, startTime, endTime )
		tickInterval = dbManager.getLogDbInterval()

		# Step 2: Determine which resolution will cover the time range that we
		# want, for now just use the lowest
		window = self.chooseResolution( prefTree.windowPrefs, tickInterval,
			startTime, endTime )

		# Step 3: Get the machines
		query = """SELECT DISTINCT(machine.ip), machine.hostname
					FROM %s_lvl_%03d stat
					JOIN %s machine ON stat.machine = machine.ip """ % \
				(constants.tblStatMachines, window.dbId,
					constants.tblSeenMachines)

		if fromTick:
			query += "AND tick > %s " % (fromTick)
		if toTick:
			query += "AND tick < %s " % (toTick)
		if ips != None and len( ips ) > 0:
			query += " AND machine.ip IN (%s) " % \
				(",".join( str( utils.inet_aton( ip ) ) for ip in ips ))

		query += " ORDER BY machine.hostname"

		utils.timeQuery( sqlLog.info, "requestMachineInfo", cursor, query )
		cursor.execute( query )
		results = cursor.fetchall()
		machineList = [ graphutils.MachineInfo( *row ) for row in results ]

		cursor.close()
		#apiLog.debug( "requestMachineInfo: Machine list: %s", machineList )
		return machineList

	def __str__( self ):
		return "<MacReq>"

	__repr__ = __str__
# -------------------------------------------------------------------------
# Section: ProcessRequester
# -------------------------------------------------------------------------
class ProcessRequester( DatabaseRequester ):
	def __init__( self, backend ):
		self.backend = backend
		self.idColumn = "process"
		self.label = "Process"
		self.seenObjTableName = constants.tblSeenProcesses
		self.seenObjIdColumn = "id"

	def getTableName( self, prefTree, type ):
		return prefTree.procPrefs[type].tableName

	def getDetails( self, procDbIds, cursor ):
		"""
		Given a list/set of process dbids, get their process info.
		"""

		if len(procDbIds) == 0:
			return []

		query = "SELECT p.id, pp.name, p.name, p.pid, m.hostname FROM %s p "\
				"JOIN %s m ON p.machine = m.ip "\
				"JOIN %s pp ON p.processPref = pp.id "\
				"WHERE p.id IN (%s) "\
				"ORDER BY p.name" % \
					(constants.tblSeenProcesses, constants.tblSeenMachines,
					constants.tblPrefProcesses, ",".join(map(str, procDbIds)))

		utils.timeQuery( sqlLog.info, "getDetails(process)", cursor, query )
		results = cursor.fetchall()
		processInfo = [graphutils.ProcessInfo(*row) for row in results]
		return processInfo


	@utils.logFunc( apiLog.info )
	def requestProcessInfo( self, logDb, user, processType, startTime,
			endTime, dbIDs = None ):
		"""
		Request details about processes for a certain user.
		"""
		# Just a few initialisations
		dbManager, prefTree = managedb.ptManager.requestDbManager( logDb )
		procPref = prefTree.procPrefs[processType]
		cursor = dbManager.getLogDbCursor()
		tickInterval = dbManager.getLogDbInterval()

		# Step 1: Get some variables from the database
		fromTick, toTick = self.getTickRange( cursor, startTime, endTime )
		window = self.chooseResolution( prefTree.windowPrefs, tickInterval,
			startTime, endTime )

		# Step 2: Get the new processes
		tableName = "%s_lvl_%03d" % (procPref.tableName, window.dbId)
		query = "SELECT DISTINCT(process) FROM %s s "\
				"JOIN %s p ON s.process = p.id " \
				"WHERE p.userid = %s " % \
				( tableName, constants.tblSeenProcesses, user )

		if fromTick:
			query += "AND tick > %s " % (fromTick)
		if toTick:
			query += "AND tick < %s " % (toTick)
		if dbIDs != None and len( dbIDs ) > 0:
			query += " AND s.process IN (%s)" % \
				(",".join(str(int(p)) for p in dbIDs))

		utils.timeQuery( sqlLog.info, "requestProcessInfo", cursor, query )
		results = cursor.fetchall()

		# Step 3: Get process details corresponding to the ids
		procIds = [r[0] for r in results]
		procList = self.getDetails( procIds, cursor )
		cursor.close()

		#apiLog.debug("Process list: %s (Type is: %s)",
		#	[proc.name for proc in procList], type( procList ) )

		return procList

	def __str__( self ):
		return "<ProcReq>"

	__repr__ = __str__
