import os, time, logging
import random
import httplib
import urllib

from turbogears import controllers, expose, redirect
from turbogears import validate, validators, identity
from turbogears import config


# BigWorld includes
import bwsetup; bwsetup.addPath( "../.." )
from pycommon import cluster
from pycommon import watcher_tree_filter as watcher
from pycommon.exceptions import ServerStateException, IllegalArgumentException
from web_console.common import module
from web_console.common import util 
from web_console.common.authorisation import Permission


log = logging.getLogger( __name__ )


# Class to represent uploaded profile dump file
class ProfilerDump( object ):

	def __init__( self, fileName, timestamp, size ):
		self.fileName = fileName
		self.timestamp = timestamp
		self.size = size;

# end class ProfilerDump


class ProfileDownloadFailure( Exception ):
	""" Raised when a request is made to a ServiceApp but no ServiceApp
	is running. """

	def __init__( self, dumpFilePath ):
		Exception.__init__( self, dumpFilePath )
		self.dumpFilePath = dumpFilePath
		

	def __str__( self ):
		return self.dumpFilePath

# end class ProfileDownloadFailure


class ProfilerController( module.Module ):

	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )
		self.addPage( "Processes", "processes" )
		self.addPage( "Recordings", "dumps" )
		self.addPage( "Help", "help" )

		self.uploadDir = config.get( 'web_console.upload_directory' )
	# __init__


	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self, **kw ):
		raise redirect( "processes", **kw )
	# index

	@identity.require( Permission( 'view' ) )
	@expose( template = 'profiler.templates.dumps' )
	def dumps( self, **kw ):
		userUploadDir = self._getUserUploadDir()

		dumpList = []
		for fileName in os.listdir( userUploadDir ):
			filePath = os.path.join( userUploadDir, fileName )
			if os.path.isfile( filePath ):
				dumpList.append( ProfilerDump ( fileName,
						time.ctime( os.path.getctime( filePath ) ), 
						os.path.getsize( filePath ) ) )

		return dict( dumps = dumpList )
	# dumps


	
	@identity.require( Permission( 'view', 'modify' ) )
	@expose()
	@util.forbidEmptyArguments
	def upload( self, uploadFile, **kw ):
		data = uploadFile.file.read()
		targetFileName = os.path.join( self._getUserUploadDir(),
									uploadFile.filename )

		f = open( targetFileName, 'wb' )
		f.write( data )
		f.close()
	
		raise redirect( "dumps", **kw )	
	# upload


	@identity.require( Permission( 'view', 'modify' ) )
	@expose()
	@util.forbidEmptyArguments
	def delete( self, fileName, **kw ):
		# Check that the user isn't trying to delete a file outside
		# of the upload directory.
		userUploadDir = self._getUserUploadDir()
		absPath = os.path.abspath( os.path.join( userUploadDir, fileName ) )
		if not absPath.startswith( userUploadDir ):
			message = "Dangerous and suspicious fileName: %s" % fileName
			log.error( message )
			raise IllegalArgumentException( message )
		elif os.path.isfile( absPath ):
			os.remove( absPath )
		else:
			raise IOError( "File not found: %s" % fileName )

		raise redirect( "dumps", **kw )	
	# delete


	@identity.require( Permission( 'view' ) )
	@expose( template = 'profiler.templates.viewdump' )
	@util.forbidEmptyArguments
	def view( self, fileName ):
		# Check that the user isn't trying to access a file outside
		# of the upload directory.
		userUploadDir = self._getUserUploadDir()
		absPath = os.path.abspath( os.path.join( userUploadDir, fileName ) )

		if not absPath.startswith( userUploadDir ):
			message = "Dangerous and suspicious fileName: %s" % fileName
			log.error( message )
			raise IllegalArgumentException( message )
		elif not os.path.isfile( absPath ):
			raise IOError( "File not found: %s" % fileName )

		c = cluster.cache.get()
		user = util.getUser( c )
		return dict( userName = user.name, fileName = fileName )
	# view

	
	@identity.require( Permission( 'view' ) )
	@expose( template = 'profiler.templates.processes' )
	def processes( self ):
		c = cluster.cache.get()
		user = util.getUser( c )

		return dict( processes = util.getProcsOfUserSortedByLabel( c ), 
					user = user )
	# processes


	@identity.require( Permission( 'view', 'modify' ) )
	@expose( template = 'profiler.templates.liveview' )
	@util.forbidEmptyArguments
	def liveview( self, machine, pid ):
		p = self._getProcByPID( machine, pid )

		# Make sure this process supports profiling
		enabledData = p.getWatcherData( "profiler/enabled" )
		if not enabledData or enabledData.value == None:
			log.error( "Failed to get watcher 'profiler/enabled'." \
					" Indicates %s doesn't support profiling." )
			raise redirect( "/error", 
					msg = "%s doesn't support profiling" % p.label() )

		# Make sure this process is compatible with WebConsole
		# This watcher was added in 2/6
		# Failing to get this indicates incompatible process version
		categoriesdData = p.getWatcherData( "profiler/controls/categories" )
		if not categoriesdData or categoriesdData.value == None:
			log.error( "Failed to get watcher 'profiler/controls/categories'." \
					" Indicates the process version is incompatible with the " \
					"WebConsole version.")
			raise redirect( "/error", 
					msg = "Cannot start Live View." \
							" %s may be of older version than WebConsole " \
							"and is incompatible. " % p.label() )
		
		return dict( machine = machine, pid = pid, processName = p.label() )
	# liveview
	
	
	@identity.require( Permission( 'view', 'modify' ) )
	@expose( "json" )
	@util.forbidEmptyArguments
	def startProfile( self, machine, pid, sortMode, exclusive, category ):
		p = self._getProcByPID( machine, pid )

		p.setWatcherValue( "profiler/sortMode", str( sortMode ) )
		p.setWatcherValue( "profiler/exclusive", str( exclusive ) )
		p.setWatcherValue( "profiler/controls/currentCategory", str( category ) )
		p.setWatcherValue( "profiler/enabled", "True" )
		
		return self._getProfileStatus( p )
	# startProfile
	
	
	@identity.require( Permission( 'view', 'modify' ) )
	@expose( "json" )
	@util.forbidEmptyArguments
	def stopProfile( self, machine, pid ):
		p = self._getProcByPID( machine, pid )

		p.setWatcherValue( "profiler/dumpProfile", "False" )
		p.setWatcherValue( "profiler/enabled", "False" )
		
		return self._getProfileStatus( p )
	# stopProfile		
				

	@identity.require( Permission( 'view', 'modify' ) )
	@expose( "json" )
	@util.forbidEmptyArguments
	def startRecording( self, machine, pid, dumpCounts ):
		try:
			dumpCounts = int( dumpCounts )
		except ValueError:
			raise IllegalArgumentException( argName="dumpCounts",
				argValue=dumpCounts,
				message="Invalid value for 'dumpCounts': %r is not an integer" \
						% dumpCounts )
		if dumpCounts < 1:
			raise IllegalArgumentException( argName="dumpCounts",
							argValue=dumpCounts,
							message="'dumpCounts' must be greater than 0" )

		p = self._getProcByPID( machine, pid )
		p.setWatcherValue( "profiler/dumpProfile", "True" )
		p.setWatcherValue( "profiler/dumpFrameCount", str( dumpCounts ) )
		
		return self._getProfileStatus( p )
	# startRecord

				
	@identity.require( Permission( 'view', 'modify' ) )
	@expose( "json" )
	@util.forbidEmptyArguments
	def cancelRecording( self, machine, pid ):
		p = self._getProcByPID( machine, pid )

		p.setWatcherValue( "profiler/dumpProfile", "False" )

		return self._getProfileStatus( p )
	# canelRecording

				
	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	@util.forbidEmptyArguments
	def profileStatus( self, machine, pid ):
		p = self._getProcByPID( machine, pid )

		return self._getProfileStatus( p )
	# profileStatus


	@identity.require( Permission( 'view', 'modify' ) )
	@expose( "json" )
	@util.forbidEmptyArguments
	def setWatcher( self, machine, pid, path, value ):
		if not path.startswith( "profiler" ):
			message = "Invalid watcher path: %s" % path
			log.error( message )
			raise IllegalArgumentException( message )

		p = self._getProcByPID( machine, pid )

		p.setWatcherValue( path, str( value ) )

		return dict( result = True )
	# setWatcher 


	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	@util.forbidEmptyArguments
	def statistics( self, machine, pid ):
		p = self._getProcByPID( machine, pid )

		stats = p.getWatcherData( "profiler/statistics" )
		if not stats or not stats.value:
			log.error( "Failed to get profiler/statistics" )
			raise Exception( "Failed to get statistics" )

		statsValues = [] 
		for line in stats:
			statsValues.append( line.value )

		return { 'statistics' : ''.join( statsValues ) }
	# statistics 


	@identity.require( Permission( 'view', 'modify' ) )
	@expose( "json" )
	@util.forbidEmptyArguments
	def getProfileDump( self, machine, dumpFilePath ):
		localServiceAddrList, remoteServiceAddrList = \
				self._getProfileDumpsHttpServiceAddr( machine )
		if not localServiceAddrList and not remoteServiceAddrList:
			log.info( "No service app is running for current user.")
			raise ProfileDownloadFailure( dumpFilePath )
		
		downloaded = False

		# try the serviceapp on the same machine first
		downloaded = self._downloadProfileDumpFromAddrList(
							localServiceAddrList, dumpFilePath )

		# try the serviceapp on other machines, this may work when the json
		# is dumped to network shared directory 
		if not downloaded:
			downloaded = self._downloadProfileDumpFromAddrList(
								remoteServiceAddrList, dumpFilePath )

		if not downloaded:
			raise ProfileDownloadFailure( dumpFilePath )

		return dict( dumpFilePath = dumpFilePath )

	# getProfileDump 


	def _getUserUploadDir( self ):
		c = cluster.cache.get()
		user = util.getUser( c )

		userUploadDir = os.path.abspath( os.path.join( self.uploadDir,
													user.name ) )
		if not os.path.exists( userUploadDir ):
			os.makedirs( userUploadDir )

		return userUploadDir

	# _getUserUploadDir


	def _getProcByPID( self, machine, pid ):
		c = cluster.cache.get()
		m = c.getMachine( machine )

		if not m:
			raise ServerStateException(
					"Machine %s appears to be offline" % machine )

		try:
			p = m.getProc( int( pid ) )
		except ValueError:
			raise IllegalArgumentException( argName="pid", argValue=pid,
				message="Invalid value for 'pid': %r is not an integer" % pid )

		if not p:
			raise ServerStateException(
					"Process %s on machine %s no longer exists"
					% ( pid, machine ) )

		return p

	# _getProcByPID


	def _getProfileStatus( self, process ):
		enabledPath = "profiler/enabled"
		sortModePath = "profiler/sortMode"
		exclusivePath = "profiler/exclusive"
		recordingPath = "profiler/dumpProfile"
		dumpFilePathPath = "profiler/dumpFilePath"
		currentCategoryPath = "profiler/controls/currentCategory"
		categoriesPath = "profiler/controls/categories"
		ticksPerSecondPath = "gameUpdateHertz"
		dumpStatePath = "profiler/dumpState"
		jsonDumpCountPath = "profiler/dumpFrameCount"
		jsonDumpIndexPath = "profiler/dumpFrameIndex"

		watcherPaths = [ enabledPath,
						sortModePath,
						exclusivePath,
						recordingPath,
						dumpFilePathPath,
						currentCategoryPath,
						categoriesPath,
						ticksPerSecondPath,
						dumpStatePath,
						jsonDumpCountPath,
						jsonDumpIndexPath ]

		watcherValues = process.getWatcherValues( watcherPaths )
		
		if not watcherValues:
			log.error( "Failed to batch query profiler status from %s", 
				process.label())
			raise Exception( "Failed to get profiler status" )

		return dict( enabled = watcherValues[ enabledPath ], 
					recording = watcherValues[ recordingPath ],
					dumpFilePath = watcherValues[ dumpFilePathPath ],
					sortMode = watcherValues[ sortModePath ],
					exclusive = watcherValues[ exclusivePath ],
					currentCategory = watcherValues[ currentCategoryPath ],
					categories = watcherValues[ categoriesPath ],
					ticksPerSecond = watcherValues[ ticksPerSecondPath ],
					dumpState = watcherValues[ dumpStatePath ],
					jsonDumpCount = watcherValues[ jsonDumpCountPath ],
					jsonDumpIndex = watcherValues[ jsonDumpIndexPath ] )
	# _getProfileStatus
	

	def _getProfileDumpsHttpServiceAddr( self, machineName ):
		c = cluster.cache.get()
		user =  util.getUser( c )
		machine = c.getMachine( machineName )

		allServiceAppProcs = user.getProcs( "serviceapp" )
		if not allServiceAppProcs:
			log.warning( "No serviceapps running for user(%s)", user.name )
			return ( None, None )

		localServiceAppProcs= machine.getProcs( "serviceapp", user.uid )
		if localServiceAppProcs:
			remoteServiceAppProcs = [ proc for proc in allServiceAppProcs \
										if not proc in localServiceAppProcs ]
		else:
			remoteServiceAppProcs = allServiceAppProcs

		localAddrList = None
		remoteAddrList = None
		watcherPath = "services/data/profile_dumps_http"
		
		if localServiceAppProcs:
			try:
				table = watcher.getFilteredTree( watcherPath, \
												localServiceAppProcs )
				localAddrList = [item[0] for item in table.values.values() \
											if item[0]]
			except Exception, ex:
				log.warning( "Watcher error for path '%s': %s", watcherPath, ex )

		if remoteServiceAppProcs:
			try:
				table = watcher.getFilteredTree( watcherPath, \
												remoteServiceAppProcs )
				remoteAddrList = [item[0] for item in table.values.values() \
											if item[0]]
			except Exception, ex:
				log.warning( "Watcher error for path '%s': %s", watcherPath, ex )

		return ( localAddrList, remoteAddrList ) 
	
	# _getProfileDumpsHttpServiceAddr


	def _downloadProfileDumpFromAddrList( self, serviceAddrList, dumpFilePath ):
		while serviceAddrList:
			serviceAddr = serviceAddrList.pop(
							random.randint( 0, len( serviceAddrList ) -1 ) )

			if self._downloadProfileDump( serviceAddr, dumpFilePath ):
				return True

		return False

	# _downloadProfileDumpFromAddrList


	def _downloadProfileDump( self, serviceAddr, dumpFilePath ):
		log.info( "Downloading profile dump %s from %s", dumpFilePath,
					serviceAddr )

		(host, port) = serviceAddr.split( ':' )
		port = int( port )

		# handling possible special characters in file name
		url = urllib.quote( "/profiledumps/" + dumpFilePath )
		httpConnection = httplib.HTTPConnection( host, port )

		try:
			httpConnection.request( 'GET', url )
		except Exception, ex:
			log.info( "No response from %s: %s", service_host, ex )
			return False

		httpResponse = httpConnection.getresponse()

		if not httpResponse.status == httplib.OK:
			log.info( "Host %s returned http status %s to request %s",
				serviceAddr, httpResponse.status, dumpFilePath )
			return False

		targetFilePath = os.path.join( self._getUserUploadDir(),
								os.path.basename( dumpFilePath ) )
		targetFile = open( targetFilePath, 'wb' )

		# read from remote host 4K at a time
		data = httpResponse.read( 4096 )
		while data:
			targetFile.write( data )
			data = httpResponse.read( 4096 )

		targetFile.close()

		try:
			# delete the original json file after upload to web console
			httpConnection.request( 'DELETE', url )
			httpResponse = httpConnection.getresponse()
			if not httpResponse.status == httplib.ACCEPTED:
				log.info( "Host %s returned http status %s to remove %s",
					serviceAddr, httpResponse.status, dumpFilePath )
		except httplib.HTTPException:
			log.info( "No response from %s", service_host )
					
		httpConnection.close()

		return True

	# _downloadProfileDump

# end class ProfilerController
