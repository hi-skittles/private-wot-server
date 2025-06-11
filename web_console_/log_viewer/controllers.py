import logging
import cherrypy
import turbogears
import sqlobject

from turbogears import controllers, expose, redirect
from turbogears import validate, validators, identity
from turbogears import widgets, config
from turbojson import jsonify

import re
import time
import threading

# BigWorld includes
import bwsetup; bwsetup.addPath( "../.." )
from pycommon import machine as machine_module
from pycommon import process as process_module
from pycommon import async_task
from pycommon.exceptions import ServerStateException
import pycommon.util
import pycommon.log_storage_interface as log_storage_interface
from pycommon.log_storage_interface.log_reader_constants \
	import ORDERED_OUTPUT_COLUMNS, DEFAULT_DISPLAY_COLUMNS, DEFAULT_CONTEXT
from pycommon.log_storage_interface.log_db_constants \
	import BACKEND_MLDB, BACKEND_MONGODB
from web_console.common import util
from web_console.common import module
from web_console.common import ajax
from web_console.common.authorisation import Permission

import model
import inspect
import encodings
from query_params import QueryParams

log = logging.getLogger( __name__ )

# Release updates to the client at least this often
MAX_UPDATE_WAIT = 1.0

# Release updates to the client when this many results are accumulated
MAX_UPDATE_SIZE = 5000

# Max number of lines to provide context in live mode
LIVE_BACKWARD_CONTEXT = 10

class LogViewer( module.Module ):

	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )
		self.addPage( "Search", "search" )
		self.addPage( "Usage", "summaries" )
		self.addPage( "Help", "help" )

		try:
			self.logReader = log_storage_interface.createReader()
		except ServerStateException, ex:
			log.error( "Failed to initialise interface to Message Logger: %s",
				str( ex ))
			raise

	# __init__


	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self, **kw ):
		raise redirect( "search", **kw )
	# index


	# --------------------------------------------------------------------------
	# Section: Pages
	# --------------------------------------------------------------------------

	@identity.require( Permission( 'view' ) )
	@expose( template = "log_viewer.templates.search" )
	def search( self, **kw ):

		# Refresh the filter dropdown information and list of users with logs.
		self.logReader.refreshLogDB()

		# Generate hostnames, component names and severities in order
		hostnames = sorted( self.logReader.getHostnames().values() )
		components = sorted( self.logReader.getComponentNames(),
							 process_module.Process.cmpByName )
		severities = [v for k, v in sorted( self.logReader.getSeverities().items(),
											key = lambda (k,v): k )]

		serveruser = util.getServerUsername()

		# Extract this user's last annotation (if any)
		try:
			results = model.lvAnnotation.select(
				model.lvAnnotation.q.userID == util.getSessionUID() )
			annotation = results[0].message

		except IndexError:
			annotation = ""

		# We need to present the time of the server as it is offset from UTC.
		# This allows the client to determine its difference for time specific
		# queries
		timezoneOffset = time.timezone
		if time.daylight and time.localtime().tm_isdst == 1:
			# A daylight savings time is defined AND it is in effect
			timezoneOffset = time.altzone

		user_categories = sorted( self.logReader.getCategoryNames() )

		message_sources = sorted( self.logReader.getSourceNames() )

		defaultQuery = self.getSavedQuery( 'default' ) or ''

		return dict(
			users = sorted( self.logReader.getUsers() ),
			hostnames = hostnames,
			components = components,
			serverTimezone = timezoneOffset,
			severities = severities,
			output_columns = ORDERED_OUTPUT_COLUMNS,
			default_columns = DEFAULT_DISPLAY_COLUMNS,
			categories = user_categories,
			message_sources = message_sources,
			mlstatus = self.logReader.isRunning(),
			annotation = annotation,
			defaultQuery = defaultQuery,
			allowContextFilter = (self.logReader.dbType == BACKEND_MLDB),
			allowMetadataFilter = (self.logReader.dbType == BACKEND_MONGODB)
		)
	# search


	@identity.require( Permission( 'view' ) )
	@expose( template = "log_viewer.templates.summaries" )
	def summaries( self, **kw ):
		"""
		Displays a table of summaries of log usage for all users.
		"""

		# TODO: This functionality needs to be abstracted to the
		# log_storage_interface
		from message_logger.message_log import MessageLog

		mlog = MessageLog( self.logReader.config )
		info = []

		for uid in mlog.getUIDs():
			try:
				userLog = mlog.getUserLog( uid )
			except:
				log.info( "Failed to get a UserLog for UID '%s'", uid )
				continue

			segments = userLog.getSegments()

			# This should only happen if a user registers a process with
			# message_logger but never sends a single log message
			if not segments:
				continue

			size = pycommon.util.fmtBytes(
				sum( [s.entriesSize + s.argsSize for s in segments] ), True )

			entries = sum( [s.nEntries for s in segments] )
			start = time.ctime( segments[0].start )
			end = time.ctime( segments[-1].end )

			t = int( segments[-1].end - segments[0].start )
			duration = pycommon.util.fmtSecondsLong( t )

			info.append( (userLog.username, size, entries, len( segments ),
						  start, end, duration ) )

		info.sort()
		return dict( info = info )
	# summaries


	@identity.require( Permission( 'view' ) )
	@expose( template = "log_viewer.templates.summary" )
	def summary( self, logUser ):

		# TODO: This functionality needs to be abstracted to the
		# log_storage_interface
		from message_logger.message_log import MessageLog

		mlog = MessageLog( self.logReader.config )
		userLog = mlog.getUserLog( mlog.getUsers()[ logUser ] )
		segments = userLog.getSegments()

		return dict( logUser = logUser, segments = segments )
	# summary

	# --------------------------------------------------------------------------
	# Section: Log querying interface
	# --------------------------------------------------------------------------

	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def fetchAsync( self, limit = 10000, live = False, queryID = None, **rawQueryParams ):
		"""
		Builds and executes an asynchronous query against the message_logger
		logs. Returns the id of the async task executing the query. Results are
		obtained by "/poll?id=<id>".
		"""
		limit = int( limit )
		responseDict = {}

		if queryID:
			try:
				logQuery = self.logReader.getQueryByID( queryID )
			except LookupError, ex:
				log.error( str( ex ) )
				raise
		else:
			# Refresh the filter dropdown information and list of users with logs.
			self.logReader.refreshLogDB()

			# process CGI params
			queryParams = QueryParams( self.logReader, **rawQueryParams )

			# perform message_logger query
			params = queryParams.getLogParams()
			log.debug( 'message_logger arguments: %r', params )

			logQuery = self.logReader.createQuery( params, resultLimit = limit )
			if queryParams.columnFilter:
				logQuery.setColumnFilter( queryParams.columnFilter )

			if queryParams.errors:
				responseDict['validationErrors'] = queryParams.errors
				responseDict['invalidParams'] = queryParams.errorParams

			# save current query
			try:
				self._saveQuery( 'most recent', queryParams )
			except Exception, ex:
				log.warning( "failed to save query: %s", str( ex ) )
				responseDict['error'] = str( ex )

		# set poll limit for QueryStatus, 0 means no limit 
		pollCountLimit = 0 
		if live:
			pollCountLimit = config.get( "web_console.log_max_poll_lines",
										5000 )

		# we have to instantiate the status here as we need the poll call back
		# for the AsyncTask. The poll call back is to implement the poll limit
		status = QueryStatus( pollCountLimit, limit, logQuery, live )
		timeoutDetails = {
			'timeout': MAX_UPDATE_WAIT,
			'callback': status.logQueryCallback,
		}

		logQuery.setTimeoutDetails( timeoutDetails )

		# In non-live mode, need slots for 'progress' and 'results'
		# TODO: Investigate the performance implications of having live
		# console queries in blocking mode (which will make response times
		# much faster but will increase load on the server I'm guessing).
		if live:
			queuesize = 0
		else:
			queuesize = 2

		# Start fetch and make sure it's running
		task = async_task.AsyncTask( queuesize, self.runQueryWithCleanup,
				logQuery, live, status, pollCallback = status.pollCallback )

		log.info( "started async query, task id = %d", task.id )
		responseDict['id'] = task.id
		responseDict['_status'] = 0

		return responseDict
	# fetchAsync


	def runQuery( self, logQuery, live, status, _async_ ):
		"""
		This is the workhorse method that runs searches and returns results to
		the client.  It must be run as an AsyncTask.
		"""
		status.setAsyncTask( _async_ )
		status.setUpdateLimit( MAX_UPDATE_SIZE, MAX_UPDATE_WAIT )

		if live:
			results = logQuery.fetchContext( contextLines = DEFAULT_CONTEXT,
											fetchForwardContext = False )
			if results:
				status.appendLogEntries( results )
				status.flush( results.size() )

		while True:

			# This loop is to handle timeouts that can occur from a narrow
			# filter, that may take longer than the accepted timeframe and
			# therefore may have not filled a page even though there are more
			# results remaining.
			while status.canFetchMore() and logQuery.moreResultsAvailable():
				# There is no need to trigger a live query resume/refresh here,
				# as it will occur below when moreResultsAvailable is called 
				# again while sleeping.
				logQuery.fetchNextResultSet( status.maxRemaining(), status )

			# Upon finishing, flush any unflushed lines, or send at least one
			# progress update (via flush) if none have been sent.
			if status.currCount() > 0 or not status.progressUpdateSent:
				status.flush()

			if live:
				# We can't wait for more results because it blocks and doesn't
				# allow us to call _async_.update() to check if we've been
				# terminated by the user.
				while not logQuery.moreResultsAvailable( refreshQuery = True ):
					_async_.update()
					time.sleep( 0.5 )

			# Non-live queries never execute this loop twice
			else:
				break
	# runQuery


	def runQueryWithCleanup( self, logQuery, live, status, _async_ ):
		"""
		This method is used to run a query but when it finishes it will cleanup
		any connections as necessary.
		"""
		try:
			try:
				self.runQuery( logQuery, live, status, _async_ )
			except _async_.TerminateException:
				if live:
					log.debug( "Live mode stopped" )
				else:
					log.debug( "Fetch terminated" )
				raise
			except:
				log.warning( "Unexpected exception in runQueryWithCleanup()" )
				raise
		finally:
			logQuery.endFetch()


	@identity.require( Permission( 'view', 'modify' ) )
	@ajax.expose
	def annotate( self, user, message ):

		# Get the message logger process running on this machine
		m = machine_module.Machine.localMachine()

		try:
			p = m.getProcs( "message_logger" )[0]

		except IndexError:
			raise ajax.Error( "message_logger isn't running on this machine!" )

		p.sendMessage( message, user )

		# Forget old annotation (if any)
		try:
			old = model.lvAnnotation.select(
				model.lvAnnotation.q.userID == util.getSessionUID() )
			old[0].destroySelf()
		except IndexError:
			pass

		# Remember this annotation
		model.lvAnnotation( user = util.getSessionUser(), message = message )

		return "Message logged at %s" % time.ctime()
	# annotate


	# --------------------------------------------------------------------------
	# Section: Saved settings management
	# --------------------------------------------------------------------------

	def getSavedQuery( self, queryId = 'default' ):

		log.debug( "retrieving query '%s'", queryId )
		savedQueries = model.lvQuery
		userId = util.getSessionUID()

		try:
			q = savedQueries.select( sqlobject.AND(
				savedQueries.q.userID == userId,
				savedQueries.q.name == queryId ) )

			return q[0].query_string

		except IndexError:
			log.info( "no saved query for user '%s' named '%s'",
				userId, queryId )
			return None
	# getSavedQuery


	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def saveQuery( self, name, **query ):
		try:
			if self.logReader.dbType == BACKEND_MLDB:
				# Refresh the MLDB tables.
				self.logReader.refreshLogDB()

			params = QueryParams( self.logReader, **query )
			self._saveQuery( name, params )
			return {}
		except Exception, ex:
			msg = "Save query '%s' failed: %s" % (name, str( ex ))
			log.warning( msg )
			return { 'warning': msg }
	# saveQuery


	def _saveQuery( self, name, queryParams ):
		""" Save the passed L{QueryParams} instance under the given name
			to the current user's saved queries. """

		log.info( "saving query '%s'", name )
		try:
			# delete existing query, if any
			old = model.lvQuery.select( sqlobject.AND(
				model.lvQuery.q.userID == util.getSessionUID(),
				model.lvQuery.q.name == name ) )
			old[0].destroySelf()

		except IndexError:
			# doesn't exist
			pass

		except UnicodeEncodeError, ex:
			log.warning( "Exception while deleting old query with name '%s': "
				"%s", name, ex )

		user = util.getSessionUser()
		queryString = queryParams.getQueryString()

		try:
			rec = model.lvQuery( user=user, name=name,
				query_string=queryString )
			log.info(
				"query '%s' saved successfully; query_string is '%s'",
				name, queryString )
		except Exception, ex:
			log.warning( "save query '%s' failed: %s", name, queryString )
			raise
	# _saveQuery


	@identity.require( Permission( 'view' ) )
	@ajax.expose
	def deleteQuery( self, name ):

		errhdr = "Delete query failed"

		if name == "default":
			raise ajax.Error, (errhdr, "Can't delete the default query")

		try:
			old = model.lvQuery.select( sqlobject.AND(
				model.lvQuery.q.userID == util.getSessionUID(),
				model.lvQuery.q.name == name ) )[0]
			old.destroySelf()

		except IndexError:
			raise ajax.Error, (errhdr, "Query %s not found" % name)

		return dict()
	# deleteQuery


	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def fetchQueries( self ):

		queries = None
		try:
			queries = list( model.lvQuery.select(
				model.lvQuery.q.userID == util.getSessionUID(),
				orderBy = "id" ) )

			if not queries:
				defaultQuery = self.getSavedQuery( 'default' )
				if defaultQuery:
					queries = [defaultQuery]
				else:
					queries = []
		except Exception, ex:
			log.warning( "Exception while fetching saved queries for user "
				"'%s': %s", util.getServerUsername(), ex )
			raise ex

		# Keying operator for queries.
		def order( rec ):
			if rec.name == "default": return -2
			if rec.name == "most recent": return -1
			return rec.name

		queries = map( dict, sorted( queries, key = order ) )

		return dict( queries = queries )
	# fetchQueries

# end class LogViewer


# class to store and update query data
class QueryStatus( object ):

	def __init__( self, pollCountLimit, maxLines, logQuery, liveMode ):
		self.lines = []
		self.totalCount = 0
		self.progressUpdateSent = False
		self.updateTime = time.time()

		self.polled = False;
		self.pollCountLimit = pollCountLimit
		self.countAfterPoll = 0

		self.maxLines = maxLines

		self.logQuery = logQuery
		self.charset = self.logQuery.logReader.getCharset()
		self.liveMode = liveMode

		self.updateLock = threading.Lock()


	def setAsyncTask( self, asyncTask ):
		self.asyncTask = asyncTask


	def setUpdateLimit( self, countLimit, timeLimit ):
		self.updateCountLimit = countLimit
		self.updateTimeLimit = timeLimit
		
		
	def appendLogEntry( self, logEntry ):
		if logEntry is None:
			return
		
		message = logEntry[ 'message' ]

		try:
			message = message.decode( self.charset )
		except UnicodeError, ex:
			log.warning( "charset decoding error: %s:\n%s", ex, message )
			message = repr( message[:-1] )[1:-1] + '\n'

		# append the converted entry to lines
		entry = { 'message': message, 'metadata': logEntry[ 'metadata' ] }
		self.lines.append( entry )
		self.totalCount += 1

		self.flushIfNecessary()


	def appendLogEntries( self, logEntries ):
		if logEntries is None:
			return

		for result in logEntries.asDicts():
			# Only live mode allows true truncating (ie. abandon any extra
			# results provided within logEntries). Only truncate if there are
			# more results coming from logEntries that we can not append.
			if self.liveMode and not self.canFetchMore():
				self.truncate()
				return

			message = result[ 'message' ]
			try:
				message = message.decode( self.charset )
			except UnicodeError, ex:
				log.warning( "charset decoding error: %s:\n%s", ex, message )
				message = repr( message[:-1] )[1:-1] + '\n'

			# append the converted entry to lines
			logEntry = { 'message': message, 'metadata': result[ 'metadata' ] }
			self.lines.append( logEntry )
			self.totalCount += 1

			self.flushIfNecessary()

		if not self.canFetchMore() and self.logQuery.moreResultsAvailable():
			self.truncate()


	def canFetchMore( self ):
		if not self.maxLines:
			return True
		return self.totalCount < self.maxLines


	def truncate( self ):
		self.flush()
		# If we are truncating, pass back the query ID so that it can be resumed
		# rather than fetching again.
		self.asyncTask.update( "truncated", self.logQuery.getID() )


	def maxRemaining( self ):
		if self.pollCountLimit and self.maxLines > 0:
			return min( self.pollCountLimit, (self.maxLines - self.totalCount) )
		elif self.pollCountLimit:
			return self.pollCountLimit
		elif self.maxLines > 0:
			return self.maxLines - self.totalCount

		return 0 # unlimited


	def currCount( self ):
		return len( self.lines )


	def logQueryCallback( self, queryObject = None ):
		# Update the progress indicator
		self.flush()


	# Flush results to client if we've accumulated enough or it's
	# been too long since we last sent something through
	def flushIfNecessary( self ):
		if len( self.lines ) >= self.updateCountLimit or \
		   time.time() - self.updateTime > self.updateTimeLimit:
			self.flush()


	def flush( self, context = None ):
		"""
		This method is a wraparound for doFlush, with the purpose of releasing
		the lock if an unexpected exception occurs.
		"""
		self.updateLock.acquire()
		try:
			self.doFlush( context )
		finally:
			self.updateLock.release()


	def doFlush( self, context = None ):
		if not self.progressUpdateSent:
			self.progressUpdateSent = True

		# make sure the update will not over flow poll limit
		if self.pollCountLimit:
			linesLen = len( self.lines )

			if self.countAfterPoll >= self.pollCountLimit:
				# already over limit
				self.lines = []
			elif (self.countAfterPoll + len( self.lines )) > \
					self.pollCountLimit:
				# will over the limit, reduce the updat size to the limit
				allowedSize = self.pollCountLimit - self.countAfterPoll
				self.lines = self.lines[ 0 : allowedSize ]

		if self.lines:
			self.asyncTask.update( "results",
						dict( lines = self.lines,
							  reverse = self.logQuery.inReverse() ) )
			self.countAfterPoll += len( self.lines )

		# We need to include the amount of context in the total
		# otherwise the client-side progress display is wrong for small
		# result sets.  The magic -1 here is to adjust down for the
		# first position that is skipped over in fetchContext().
		try:
			conlen = 0
			if context:
				conlen = max( context - 1, 0 )
			progress = [ x + conlen for x in self.logQuery.getProgress() ]
		except NotImplementedError, ex:
			# DB does not support progress reporting. Simply report the number
			# of lines displayed as the number of lines seen.
			progress = [ self.totalCount, 0 ]

		if not progress:
			progress = [ self.totalCount, 0 ]

		progress.append( self.logQuery.moreResultsAvailable() )

		self.asyncTask.update( "progress",
						[ self.logQuery.getID(), self.totalCount ] + progress )

		self.lines = []
		self.updateTime = time.time()


	def pollCallback( self ): 
		self.updateLock.acquire()
		self.countAfterPoll = 0
		self.updateLock.release()

# end class QueryStatus

# controllers.py
