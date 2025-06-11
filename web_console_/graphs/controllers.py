
import logging
import sys
import os.path
import subprocess

from turbogears import expose, identity, redirect, url, config

# BigWorld modules
import bwsetup;
bwsetup.addPath( "../.." )

from web_console.common import module
from web_console.common.authorisation import Permission
from pycommon.exceptions import ServerStateException, ConfigurationException

from stat_logger import prefxml
from stat_logger.model.carbon_store import CarbonStore

log = logging.getLogger( __name__ )

STAT_LOGGER_SCRIPT_NAME = "stat_logger.py"


class GraphsController( module.Module ):
	""" Implements the WebConsole Graphs module. """

	def __init__( self, *args, **kw ):
		if not config.get( 'web_console.graphs.graphite_host' ):
			raise ConfigurationException(
				"No server hostname defined for required configuration key "
				"'web_console.graphs.graphite_host'. A valid Graphite service "
				"is required for the Graphs module to function." )

		module.Module.__init__( self, *args, **kw )
		self.addPage( "Processes", "by_process" )
		self.addPage( "Machines", "by_machine" )
		self.addPage( "Help", "help" )
	# __init__


	@identity.require( Permission( 'view' ) )
	@expose()
	def index( self ):
		raise redirect( url( "by_process" ) )
	# index


	@identity.require( Permission( 'view' ) )
	@expose( "graphs.templates.dygraph" )
	def render( self, **kwargs ):
		isStatLoggerRunning, isCarbonEnabled, isCarbonRunning = \
			self.getStatLoggerCarbonStatus()
		
		kwargs[ "isStatLoggerRunning" ] = isStatLoggerRunning
		kwargs[ "isCarbonEnabled" ] = isCarbonEnabled
		kwargs[ "isCarbonRunning" ] = isCarbonRunning

		return kwargs
	# render


	by_machine = render
	by_process = render

	@expose( "xml", content_type="text/plain" )
	def prefs( self, **kwargs ):
		""" Serves the StatLogger preferences.xml file as given by WebConsole
		config key 'stat_logger.preferences'. """

		try:
			statLoggerPrefs = self.getPrefFilePath()

			return open( statLoggerPrefs ).read()
		except Exception, ex:
			log.warning( "Failed to read stat_logger preferences: %s", ex )
			return ''
	# prefs
	
	
	# Get the status of StatLogger and Carbon
	def getStatLoggerCarbonStatus( self ):
		isStatLoggerRunning = False
		isCarbonEnabled = False
		isCarbonRunning = False

		prefFilePath = self.getPrefFilePath()
		if prefFilePath:
			prefFilePath = os.path.abspath( prefFilePath )
			
			isStatLoggerRunning = self.isStatLoggerRunning( prefFilePath )
			isCarbonEnabled, isCarbonRunning = self.getCarbonStatus(
														prefFilePath )
		
		return ( isStatLoggerRunning, isCarbonEnabled, isCarbonRunning )


	# Check whether StatLogger is running by ps|grep preference file path
	# This wouldn't work if the configuration file is specified in relative path
	# format and there is no good way to deal with this case. Fortunately, for
	# production, it would be always absolute path.
	def isStatLoggerRunning( self, prefFilePath ):
		command = "ps -efww|grep '\-\-config\-file %s'" % prefFilePath

		try:
			psProc = subprocess.Popen( command,
										shell = True,
										stdout = subprocess.PIPE,
										stderr = subprocess.PIPE )
			out, err = psProc.communicate()

			# check if stat_logger.py in th output of ps/grep command
			if out and STAT_LOGGER_SCRIPT_NAME in out:
				return True

			if err:
				log.error( "Error when checking StatLogger status: %s", err )
		except Exception, ex:
			log.error( "Exception when running Popen: %s", ex )

		return False


	# Check whether carbon enabled or running by testing connection
	def getCarbonStatus( self, prefFilePath ):
		isCarbonEnabled = False
		isCarbonRunning = False

		try:
			options, prefTree = prefxml.loadPrefsFromXMLFile( prefFilePath )
		except prefxml.StatLoggerPrefError, e:
			log.error( "Error in preference file '%s':\n%s", prefFilePath, e )
			return ( isCarbonEnabled, isCarbonRunning )
		
		# Carbon is not configured or not enabled
		if not options.carbonStoreConfig or \
				not options.carbonStoreConfig.enabled:
			return ( isCarbonEnabled, isCarbonRunning )
		else:
			isCarbonEnabled = True

		# Connection was successful
		if CarbonStore.testConnection( options.carbonStoreConfig ):
			isCarbonRunning = True

		return ( isCarbonEnabled, isCarbonRunning )


	# Get the StatLogger preference file path
	def getPrefFilePath( self ):
		statLoggerPrefs = config.get( 'stat_logger.preferences', '' )

		if statLoggerPrefs and not os.path.isfile( statLoggerPrefs ) and \
			(statLoggerPrefs[ 0 ] != os.path.sep):
			statLoggerPrefs = os.path.join(
				os.path.dirname( os.path.abspath( sys.argv[ 0 ] ) ),
				statLoggerPrefs )

		return statLoggerPrefs


# end of class GraphsController

# controllers.py

