import logging
import os
import socket
import struct
import threading
import time
import re
import cPickle as pickle

from cherrypy import request, response
from cherrypy.filters.basefilter import BaseFilter
import turbogears

from pycommon import proc_reader
from pycommon.exceptions import ConfigurationException

log = logging.getLogger( __name__ )

CONFIG_ANALYTICS_ENABLED_KEY = 'web_console.analytics.on'
CONFIG_ANALYTICS_HOST = 'web_console.analytics.carbon_host'
CONFIG_ANALYTICS_PORT = 'web_console.analytics.carbon_port'

DEFAULT_STAT_CACHE_TIMEOUT = 1

class AnalyticsFilter( BaseFilter ):
	"""
	CherryPy filter that inserts into the HTTP request lifecycle to log HTTP
	request and process system information to a Graphite/Carbon endpoint.
	"""


	def __init__( self ):
		log.info( "%s loaded", self.__class__.__name__ )

		getConfig = turbogears.config.get

		# lazily create 1 connection per thread
		self.sockets = {}

		assert getConfig( CONFIG_ANALYTICS_ENABLED_KEY )
		self.carbonHost = host = getConfig( 'web_console.analytics.carbon_host' )
		self.carbonPort = port = getConfig( 'web_console.analytics.carbon_port' )
		self.carbonService = (host, port)
		self.retriedCarbonTimes = 0
		self.nextTryCarbonTime = 0

		if not host:
			raise ConfigurationException(
				"No host provided for config key '%s'", CONFIG_ANALYTICS_HOST )

		if not port:
			raise ConfigurationException(
				"No port provided for config key '%s'", CONFIG_ANALYTICS_PORT )

		wcHost = self.toCarbonMetricString( socket.gethostname(), stripFrom = '.' )
		self.metricPrefix = 'web_console.machine_%s' % wcHost
		log.debug( "using metric prefix: %s", self.metricPrefix )

		# Test the carbon configuration (which will output a non-critical error
		# if it is unable to connect).
		carbonSocket = self.getCarbonSocket()
		del carbonSocket


		# The process stats cache timeout can be increased to reduce the number
		# of file accesses to /proc. This should not be increased beyond the
		# shortest carbon aggregation interval for WebConsole metrics.
		proc_reader.statsCache.timeout = getConfig(
			'web_console.analytics.stat_cache_timeout',
			DEFAULT_STAT_CACHE_TIMEOUT)


		# Get an initial, non-cached set of cpu usage statistics to compare
		# against. This is non-cached so that the first request to the cache in
		# recordMetrics will get another set of stats regardless of the timeout
		# period.
		pid = os.getpid()
		self.lastProcessStats = proc_reader.readProcessStats( pid )
		self.lastSystemStats = proc_reader.readSystemStats()
	# __init__


	def on_start_resource( self ):
		""" Called before the request header has been read/parsed"""

		if not self.shouldRecordMetricsForRequest():
			return

		# log.debug( "on_start_resource: %s", request.path )
		request._request_start_time = time.time() * 1000
	# before_request_body


	def on_end_request( self ):
		""" Called when the server closes the request. """

		if not self.shouldRecordMetricsForRequest():
			return

		# skip logging info to carbon until the specified time
		if time.time() < self.nextTryCarbonTime:
			log.warning( "Carbon server seems down, wait until %s to retry",
				time.ctime( self.nextTryCarbonTime ) )
			return

		# log.debug( "on_end_request: %s", request.path )

		carbonSocket = self.getCarbonSocket()
		if carbonSocket is None:
			self.retriedCarbonTimes += 1

			log.warning( "Couldn't get socket, skipping metric, tried %d times",
				self.retriedCarbonTimes )

			# if connect to carbon failed 5 times then wait one minute to retry
			if self.retriedCarbonTimes > 4:
				self.nextTryCarbonTime = time.time() + 60
				self.retriedCarbonTimes = 0

			return

		self.retriedCarbonTimes = 0
		self.nextTryCarbonTime = 0

		self.recordMetrics( carbonSocket )
	# on_end_request


	def getCarbonSocket( self ):

		# cherrypy makes use of a private threading API method
		# `threading._get_ident()` as a proxy for a real thread id (which is
		# introduced in python 2.6). using same method here for compatibility.
		currentThreadId = threading._get_ident()
		carbonSocket = self.sockets.get( currentThreadId, None )

		if carbonSocket is None:
			try:
				carbonSocket = socket.socket()
				carbonSocket.settimeout( 1.0 )
				carbonSocket.connect( self.carbonService )
				self.sockets[currentThreadId] = carbonSocket
				log.info(
					"Thread %s connected to Carbon service %s:%s",
					currentThreadId, self.carbonHost, self.carbonPort )
			except IOError, ex:
				log.error( "Failed to create socket: %s", str( ex ) )
				return None
			except Exception, ex:
				log.error( "Failed to connect to carbon server (%s, %s): %s",
					self.carbonHost, self.carbonPort, str( ex ) )
				if carbonSocket:
					carbonSocket.close()
				return None

		return carbonSocket
	# getCarbonSocket


	def recordMetrics( self, sock ):
		""" Record a set of metrics for the current HTTP request. """

		metrics = []
		now = time.time() # epoch seconds
		elapsed = (now * 1000) - request._request_start_time # msec

		# request-specific metric(s)
		remoteHost = request.remote_host
		if not remoteHost:
			remoteHost = request.remote_addr
			remoteHost = re.sub( '^.*:', '', remoteHost )
			remoteHost = self.toCarbonMetricString( remoteHost )
		
		if hasattr( request, 'user_name' ):
			userName = self.toCarbonMetricString( request.user_name or '' )
		else:
			userName = self.toCarbonMetricString( '' )


		requestMetric = "%s.client_%s.user_%s.response_%s.path%s" % (
			self.metricPrefix,
			remoteHost,
			userName,
			response.status[0:3],
			self.toCarbonMetricString( request.path, stripTrailingChars = '/' )
		)

		metrics.append( (requestMetric, (now, elapsed)) )
		log.debug( "%s = %s", requestMetric, elapsed )

		cache = proc_reader.statsCache.get( pid = os.getpid() )

		# Save on lookup overheads by saving a local copy of class member dicts
		processStats = cache.processStats
		systemStats = cache.systemStats
		lastProcessStats = self.lastProcessStats
		lastSystemStats = self.lastSystemStats

		# calculate time worked between requests
		totalWorked = ((processStats[ 'processJiffies' ] -
							lastProcessStats[ 'processJiffies' ]) +
						(processStats[ 'childJiffies' ] -
							lastProcessStats[ 'childJiffies' ]))
		systemWorked = (systemStats[ 'totalWorked' ] -
			lastSystemStats[ 'totalWorked' ])
		systemWait = (systemStats[ 'totalWait' ] -
			lastSystemStats[ 'totalWait' ])
		systemIdle = (systemStats[ 'totalIdle' ] -
			lastSystemStats[ 'totalIdle' ])
		systemTotal = systemWorked + systemIdle + systemWait

		# Only calculate and record new system metrics if we have a new System
		# Total to calculate against (ie. the difference between the last check
		# and this check is non-zero)
		if systemTotal:
			processCPUPercent = (float( totalWorked ) / systemTotal) * 100
			systemWaitPercent = (float( systemWait ) / systemTotal) * 100
			systemIdlePercent = (float( systemIdle ) / systemTotal) * 100
			processMemoryPercent = \
				(processStats[ 'vsize' ] / cache.memTotal) * 100

			# once calculations are completed we can overwrite lastProcessStats
			self.lastProcessStats = processStats
			self.lastSystemStats = systemStats

			# process CPU (system)
			cpuMetric = "%s.stat_Process_CPU" % self.metricPrefix
			metrics.append( (cpuMetric, (now, processCPUPercent)) )
			log.debug( "%s = %s", cpuMetric, processCPUPercent )

			# process mem
			memMetric = "%s.stat_Process_Memory" % self.metricPrefix
			metrics.append( (memMetric, (now, processMemoryPercent)) )
			log.debug( "%s = %s", memMetric, processMemoryPercent )

			# system Idle
			cpuMetric = "%s.stat_System_Idle" % self.metricPrefix
			metrics.append( (cpuMetric, (now, systemIdlePercent)) )
			log.debug( "%s = %s", cpuMetric, systemIdlePercent )

			# system Wait
			cpuMetric = "%s.stat_System_Wait" % self.metricPrefix
			metrics.append( (cpuMetric, (now, systemWaitPercent)) )
			log.debug( "%s = %s", cpuMetric, systemWaitPercent )

		return self.sendMetrics( sock, metrics )
	# recordMetrics


	def sendMetrics( self, sock, metrics ):
		""" Send given metrics list to given connected socket. """

		payload = pickle.dumps( metrics )
		header = struct.pack( "!L", len( payload ) )
		message = header + payload

		try:
			sock.sendall( message )
			log.info( "Successfully wrote %d bytes to Carbon", len( message ) )
			return len( message )

		except Exception, ex:
			log.exception(
				"Failed to write data to Carbon service %s:%s",
				self.carbonHost, self.carbonPort )

			sock.close()
			currentThreadId = threading._get_ident()
			del self.sockets[currentThreadId]

			return
	# sendMetrics


	def shouldRecordMetricsForRequest( self ):
		""" Returns `True` if the current request should have metrics logged. """

		getConfig = turbogears.config.get

		# don't apply to static assets
		if getConfig( 'static_filter.on', False ):
			return False

		# if response.headers.get( 'Content-Type', '' ).startswith( 'image' ):
		# 	return False

		if getConfig( 'web_console.analytics.on', False ):
			return True

		return False
	# shouldRecordMetricsForRequest


	def toCarbonMetricString( self, string,
		replaceMatching = '[\-\W\s]', replaceWith = '_', stripFrom = None,
			stripTrailingChars = None ):
		""" Returns a version of the passed string that is compatible with
		Carbon's metric naming conventions.

		If `stripFrom` is provided then remove this string and everything after
		it.

		If `stripTrailingChars` is provided then strip all of the matching
		chars from the end.

		Then replace characters matching `replaceMatching` with the string
		given by `replaceWith`.
		"""

		if stripFrom:
			i = string.find( stripFrom )
			if i > -1:
				string = string[0 : i]

		if stripTrailingChars:
			i = string.rstrip( stripTrailingChars )

		return re.sub( replaceMatching, replaceWith, string )
	# toCarbonMetricString

# end class AnalyticsFilter

# analytics_filter.py

