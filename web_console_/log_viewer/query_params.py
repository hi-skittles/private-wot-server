
import re
import time
import logging
import urllib

# BigWorld includes
import bwsetup;
bwsetup.addPath( "../.." )
import pycommon.util
from pycommon.exceptions import QueryParamException
from pycommon.log_storage_interface.log_reader_constants \
	import ORDERED_OUTPUT_COLUMNS, DEFAULT_DISPLAY_COLUMNS, PRE_INTERPOLATE
from web_console.common import util

log = logging.getLogger( __name__ )


class QueryParams( object ):
	""" Handles the conversion of query filter parameters to abstract
		log_storage_interface arguments.

		Valid Parameters:

			context              lines to include around matching lines
			show                 (list of str) columns to include in output -
			                     see L{ORDERED_OUTPUT_COLUMNS}.
			queryTime            (str|formatted date) start time range, eg:
			                     "server startup", or "Mon 11 Feb 2013 11:57:56.317"
			period               (str|formatted date) end time range.
			periodValue          (int) number of periodUnit's
			periodUnit           (str) unit of time, eg: "hours"
			host                 (str) machine hostname
			serveruser           (str)
			pid                  (int) process ID
			appid                (int) app ID
			procs                (list of str) process (component) names as given
			                     by L{logReader.getComponentNames()}.
			source               (list of str) source code of log line (C++|python)
			category             (list of str) category names
			severity             (list of str) log level names
			message              (str) free text or regex
			exclude              (str) free text|regex to exclude
			casesens             (bool) message & exclude respect case
			regex                (bool) message & exclude are regexes
			metadata_key         (str) metadata key
			metadata_value       (str) metadata value
			negate_procs         (bool)
			negate_severity      (bool)
			negate_category      (bool)
			negate_source        (bool)
			negate_host          (bool)
			negate_serveruser    (bool)
			negate_pid           (bool)
			negate_appid         (bool)
			negate_message       (bool)
			negate_metadata_key  (bool)
			negate_metadata_value(bool)
	"""

	def __init__( self, logReader, **queryParams ):
		self.logReader = logReader
		self.rawParams = queryParams
		self.params = {}
		self.columnFilter = None

		# param validation errors, key is param name, value is the param value
		# that failed validation
		self.errorParams = {}

		# list of param validation error messages
		self.errors = []

		self.addFilters( **queryParams )

	# __init__


	def getQueryString( self ):
		""" Return a serialised string form of query params. Parameters that have
		an array of values are serialised into multiple parameters, eg:
		`show=process&show=date`. """
		return urllib.urlencode( self.rawParams, doseq=True )
	# getQueryString


	def getContext( self ):
		""" Returns the number of log lines to be included
			around each matching log line. """
		context = self.params.get( 'context', 0 )
	# getContext


	def getLogParams( self ):
		return self.params
	# getLogParams


	def addFilters(
		self,
		context = 0,
		show = DEFAULT_DISPLAY_COLUMNS,
		queryTime = u'server startup',
		period = u'to present',
		periodValue = None,
		periodUnit = None,
		host = "",
		serveruser = None,
		pid = 0,
		appid = 0,
		procs = (),
		source = (),
		category = (),
		severity = (),
		message = "",
		exclude = "",
		casesens = False,
		regex = False,
		metadata_key = None,
		metadata_value = None,
		metadata_condition = None,
		metadata_value_type = None,
		negate_procs			= False,
		negate_severity     	= False,
		negate_category     	= False,
		negate_source       	= False,
		negate_host         	= False,
		negate_serveruser   	= False,
		negate_pid          	= False,
		negate_appid        	= False,
		negate_message      	= False,
		**rest
	):
		""" Add query filter(s) to the current collection of filters. See class
			documentation for info about parameter names. """

		if rest:
			log.info( "Unhandled params: %r", rest )

		charset = self.logReader.getCharset()

		# Dictionary we'll populate with optional args for the C++ fetch() call
		params = self.params

		### param 'context' - an MLDB-only param
		try:
			_context = int( context )
			if context:
				params['context'] = min( 50, _context )
		except:
			log.warning( "Invalid 'context' value: '%r'", context )

		### param "serveruser"
		# defaults to current server user
		if not serveruser:
			serveruser = util.getServerUsername()

		if serveruser not in self.logReader.getUsers():
			raise QueryParamException(
				"Server user '%s' does not have any logs." % serveruser,
				paramName = 'serveruser', paramValue = serveruser )

		if serveruser:
			params['serveruser'] = serveruser

		### params "message", "exclude"
		# convert incoming text strings from utf-8, which should be enforced by
		# TurboGears KID templates, to the encoding of logs.
		if self.logReader.getCharset() != "utf-8":
			message = message.decode( "utf-8" ).encode(
												self.logReader.getCharset() )
			exclude = exclude.decode( "utf-8" ).encode(
												self.logReader.getCharset() )

		# Escape metachars in pattern if not using regexes
		if not regex:
			message = re.escape( message )
			exclude = re.escape( exclude )

			# need to unescape any chars in search strings that python has
			# escaped but which are _not_ regarded as regex metachars by
			# query_params.cpp
			# TODO: implement exact string matching in query_params.cpp
			message = message.replace( r'\<', '<' )
			exclude = exclude.replace( r'\<', '<' )

			message = message.replace( r'\>', '>' )
			exclude = exclude.replace( r'\>', '>' )

			message = message.replace( r"\'", "'" )
			exclude = exclude.replace( r"\'", "'" )

			message = message.replace( r"\`", "`" )
			exclude = exclude.replace( r"\`", "`" )

		if negate_message and message:
			# negating 'message' takes precedence over any 'exclude' value
			params['exclude'] = message
			params['message'] = ""
		else:
			params['message'] = message
			params['exclude'] = exclude

		### param: queryTime
		params['start'] = queryTime

		### params: period, periodValue, periodUnit
		logPeriod = period
		try:
			if periodValue:
				periodValue = float( periodValue or 0 )
				periodUnit = {
					'seconds': 1,
					'minutes': 60,
					'hours'  : 60 * 60,
					'days'   : 60 * 60 * 24
				}[periodUnit]

			if period == 'forwards':
				logPeriod = "+" + str( periodValue * periodUnit )
			elif period == 'backwards':
				logPeriod = "-" + str( periodValue * periodUnit )
			elif 'beginning' in period:
				logPeriod = 'to beginning'
			elif period == 'to present':
				logPeriod = 'to present'
			elif period == 'either side':
				logPeriod = str( periodValue * periodUnit )
			else:
				logPeriod = period
		except:
			# pass
			log.exception(
				"period* arguments ignored due to exception, " \
				"using default period 'to present'" )
			logPeriod = 'to present'

		params["period"] = logPeriod

		### param 'procs' -- filter by process type
		if procs:
			if negate_procs:
				params['negate_procs'] = True

			params['procs'] = procs

		### param 'source' -- filter by message source (c++ | python)
		if source:
			if negate_source:
				params['negate_source'] = True

			params['source'] = source

		### param 'severity' -- filter by log message severity
		if severity:
			if negate_severity:
				params['negate_severity'] = True

			params['severities'] = severity

		### param 'category' -- filter by log message category
		if category:
			if negate_category:
				params['negate_category'] = True

			params['categories'] = category

		### param 'interpolate' - an MLDB-only param
		params['interpolate'] = PRE_INTERPOLATE

		### param 'pid' -- filter by process ID
		try:
			params['pid'] = int( pid )
			if negate_pid:
				params['negate_pid'] = True
		except:
			# no valid pid arg
			self.addParamError(
				 "Invalid process ID value '%s'" % pid,
				paramName = 'pid', paramValue = pid )

		### param 'appid' -- filter by component appID
		try:
			params['appid'] = int( appid )
			if negate_appid:
				params['negate_appid'] = True
		except:
			# no valid appid arg
			self.addParamError(
				 "Invalid App ID '%s'" % appid,
				paramName = 'appid', paramValue = appid )

		### param 'host'
		if host:
			params['host'] = host.strip().encode( charset )
			if negate_host:
				params['negate_host'] = True

		### param 'caseSens'
		if casesens:
			params['casesens'] = True
		else:
			params['casesens'] = False

		if not metadata_key and not metadata_value:
			if metadata_condition == 'exist' \
					or metadata_condition == 'not_exist':
				self.addParamError( 
					"Metadata key can't be blank",
					paramName = 'metadata_value', 
					paramValue = metadata_value )
			elif metadata_condition == 'is' \
					or metadata_condition == 'is_not':
				self.addParamError( 
					"Metadata key and value can't be blank",
					paramName = 'metadata_value', 
					paramValue = metadata_value )
		else:
			### param 'metadata_key'
			if metadata_key:
				params['metadata_key'] = \
					metadata_key.strip().encode( charset )
				if metadata_condition == "not_exist":
					params['negate_metadata_key'] = True
				else:
					params['negate_metadata_key'] = False

				if metadata_condition == "is_not":
					params['negate_metadata_value'] = True
				elif metadata_condition == "is":
					params['negate_metadata_value'] = False

			### param 'metadata_value'
			if metadata_value:
				if not metadata_key:
					self.addParamError( 
						"Metadata value requires a metadata key",
						paramName = 'metadata_value', 
						paramValue = metadata_value )
				else:
					if metadata_value_type == 'number':
						try:
							params['metadata_value'] = \
								float( metadata_value )
						except ValueError:
							self.addParamError( 
								'Metadata value is not a number',
								paramName = 'metadata_value_type',
								paramValue = metadata_value_type )
					else:
						params['metadata_value'] = \
							metadata_value.strip().encode( charset )
					if metadata_condition == "is_not":
						params['negate_metadata_value'] = True
					elif metadata_condition == "is":
						params['negate_metadata_value'] = False

		# determine which columns will be included in output
		if show:
			self.columnFilter = show
	# addFilters


	def addParamError( self, message, paramName, paramValue ):
		log.warning( message )
		self.errors.append( message )
		self.errorParams[paramName] = paramValue
	# addParamError


# query_params.py

