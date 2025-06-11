
import httplib
import logging
import time
import cherrypy
import turbogears
import simplejson as json
import socket

from turbogears import controllers, expose, redirect
from turbogears import identity
from cherrypy import request

# BigWorld modules
import bwsetup;
bwsetup.addPath( "../.." )

from web_console.common import module, util
from web_console.common.authorisation import Permission
from pycommon.exceptions import ServerStateException
from pycommon import cluster
from pycommon import watcher_tree_filter as watcher
from cell_app_mgr_talker import CellAppMgrTalker
from cell_talker import CellTalker


#: Integer which controls the number of spaces used to indent pretty-printed
#: json output from simplejson. A value of None produces the most compact
#: form possible.
JSON_INDENT_SPACES = None

#: Max time in seconds to cache a CellAppMgrTalker IP addr. Set to 0 to disable cache.
CELLAPPMGR_CACHE_TTL = 10

#: Max time in seconds to cache a list of IPs to serviceapps running the
#: HTTPResTreeService, used for spaceviewer background tiles.
TILE_CACHE_TTL = 60 * 15 # 15 minutes

log = logging.getLogger( __name__ )


def serialiseObjectToJson( obj ):
	""" Convert arbitrary objects to a python dict prior to JSON serialisation """

	if hasattr( obj, "__json__" ):
		return obj.__json__()
	elif hasattr( obj, "__dict__" ):
		return obj.__dict__
	else:
		return TypeError( repr( obj ) + " is not JSON serializable" )
# serialiseObjectToJson


class TimedCache( object ):
	"""
	Simple dict-based cache that expires keys/values after a given time.
	No locking done; not thread-safe.
	"""

	def __init__( self, ttl = 10 ):

		#: Dict of cacheKey -> [ lastAccessedTime, cachedValue ]
		self.cache = {}

		#: Max time-to-live for a cached value in seconds.
		self.ttl = ttl
	# __init__


	def __len__( self ):
		return len( self.cache )
	# __len__


	def get( self, key, default = None ):
		"""
		Attempt to get cached value. Returns default value (None unless specified)
		if absent, otherwise returns the value associated with key.
		"""
		now = time.time()
		self._removeExpired( now )

		cacheEntry = self.cache.get( key )
		if not cacheEntry:
			return default

		value = cacheEntry[ 2 ]
		# log.debug( "returning cached '%r' -> %r", key, value )
		cacheEntry[ 0 ] = now

		return value
	# get


	def getAge( self, key ):
		""" Returns number of secs since given key was last set. """
		now = time.time()
		self._removeExpired( now )

		cacheEntry = self.cache.get( key )
		if not cacheEntry:
			return 0

		return now - cacheEntry[ 1 ]
	# getAge


	def put( self, key, value ):
		"""
		Add value to cache, overwriting any existing value associated with key.
		Identical semantics as dict.__setitem__( key, value ).
		"""
		now = time.time()
		log.debug( "caching '%r' -> %r", key, value )
		self.cache[ key ] = [ now, now, value ]
	# put


	def clear( self ):
		"""
		Clear cache of all cached items.
		"""
		self.cache.clear()
	# clear


	def _removeExpired( self, now = time.time() ):
		expiry = now - self.ttl
		for key, value in self.cache.items():
			lastAccessed = value[ 0 ]
			if lastAccessed < expiry:
				log.debug( "removing expired key '%s'", key )
				del self.cache[ key ]
	# _removeExpired

# end of class TimedCache


class SpaceViewerException( Exception ):

	def __init__( self, message, action="error" ):
		Exception.__init__( self, message )
		self.message = message
		self.action = action
	# __init__


	def __json__( self ):
		return {
			"error": self.message,
			"action": self.action
		}
	# __json__

# end class SpaceViewerException


class SpaceViewerController( module.Module ):
	"""
	Provides for:
	1) Kid template renders for "spaces overview", "space detail", and "help"
	pages.

	2) JSON-formatted data that furnish the above with:
		* the list of active spaces for the current web user
		* the entity type id: name dict for a space
		* space data for a space, including BSP, cell, and entity info
	"""


	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )

		# Navigation menu entries
		self.addPage( "Spaces", "spaces" )
		self.addPage( "Help", "help" )

		if CELLAPPMGR_CACHE_TTL:
			#: Cache (IP, port) for L{CellAppMgrTalker}s by BW server username.
			self.cellAppMgrCache = TimedCache( ttl = CELLAPPMGR_CACHE_TTL )

	# __init__


	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self ):
		raise redirect( turbogears.url( "spaces" ) )
	# index


	@identity.require( identity.not_anonymous() )
	@expose( "json" )
	def api( self, *args, **kwargs ):
		"""
		Delegates method calls on controller in order to return JSON.
		Allows methods to be called as '/path/to/controller/api/method', and
		avoids requiring the 'tg_format=json' param.
		"""
		path = cherrypy.request.path
		relPath = path[ path.index( 'api/' ) + len("api/"): ]
		methodName = 'get' + relPath.capitalize()

		method = getattr( self.__class__, methodName, None )
		if callable( method ):
			return method( self, **kwargs )
		else:
			if config.get( 'server.environment' ) == 'development':
				log.warn( "class %s has no api method '%s'", self.__class__, methodName )
				return { 'error': "No method '%s'" % methodName }
			else:
				raise cherrypy.HTTPError( 403 ) # forbidden
	# api


	@identity.require( Permission( 'view' ) )
	@expose( "kid:space_viewer.templates.show_spaces" )
	def spaces( self, *args, **queryPredicates ):
		return {}
	# spaces


	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def getSpaces( self, **queryPredicates ):
		"""
		Generates a JSON-friendly dict of data returned L{querySpaces}.
		"""
		seq = queryPredicates.get( '_', 0 )
		try:
			(sortedFilteredSpaces, filteredSpaces, spaces) = self.querySpaces( **queryPredicates )
		except Exception, ex:
			log.info( "Failed to lookup spaces: %s", str( ex ) )
			return {
				"error": str( ex ),
				"spaceList": [],
				'sEcho': seq,
				'iTotalRecords': 0,
				'iTotalDisplayRecords': 0
			}

		if spaces:
			return {
				"spaceList": sortedFilteredSpaces,
				'sEcho': seq,
				'iTotalRecords': len( spaces ),
				'iTotalDisplayRecords': len( filteredSpaces )
			}
		else:
			return {
				"info": "BigWorld server is running but no spaces are loaded",
				"spaceList": [],
				'sEcho': seq,
				'iTotalRecords': 0,
				'iTotalDisplayRecords': 0
			}
	# getSpaces


	@identity.require( Permission( 'view' ) )
	@expose( "kid:space_viewer.templates.spaceviewer_canvas" )
	def space( self, spaceId, *args ):
		spaceId = int( spaceId )

		numServiceApps = 0
		serviceApps = self._initServiceAppCache()
		if serviceApps:
			numServiceApps = len( serviceApps )

		return {
			"spaceId": spaceId,
			"serviceapps": numServiceApps }
	# space


	@identity.require( Permission( 'view' ) )
	def resources( self, *args, **kwargs ):
		"""
		Serves resources from the 'res' tree of the running Bigworld server
		by reverse-proxying the "HTTPResTreeService" of running serviceapps.
		"""

		path = cherrypy.request.path
		relPath = path[ path.index( 'resources/' ) + len("resources/"): ]

		if not relPath:
			raise cherrypy.HTTPError( 403 ) # forbidden

		service_host = self.getNextTileServiceIp()
		if not service_host:
			raise cherrypy.HTTPError(
				404, "No ServiceApps are available to service the request" )

		(addr, port) = service_host.split( ':' )
		url = "/res/" + relPath
		if port:
			port = int( port )
		else:
			port = 80

		log.info( "Reverse proxying request %s to %s:%i%s", path, addr, port, url )
		h = httplib.HTTPConnection( addr, port )

		try:
			h.request( 'GET', url )
		except Exception, ex:
			# assume serviceapp is gone, so try again until no serviceapps
			log.info( "No response from %s: %s, retrying...", service_host, ex )
			cacheWasEmpty = not self._removeFromServiceAppCache( service_host )
			if cacheWasEmpty:
				raise cherrypy.HTTPError(
					404, "No ServiceApps are available to service the request" )
			else:
				return self.resources( *args, **kwargs )

		r = h.getresponse()

		if not r.status == httplib.OK:
			log.info( "Host %s returned http status %s to request %s",
				service_host, r.status, path )
			raise cherrypy.HTTPError( r.status )

		response = cherrypy.response
		# list of (header, value) tuples
		for header, value in r.getheaders():
			if header in ('Server'):
				continue
			response.headers[ header ] = value

		# remove turbogears session cookies; they are superfluous on images
		# and some user-agents will complain about or even filter them
		del response.headers[ 'Set-Cookie' ]

		# read from remote host 4K at a time
		def body():
			chunk = r.read( 4096 )
			while chunk:
				yield chunk
				chunk = r.read( 4096 )

			h.close()
			raise StopIteration()
		# body

		return body()

	# resources
	resources.exposed = True


	@identity.require( Permission( 'modify' ) )
	@expose( "json" )
	def setCellAppMgrWatcher( self, path, value ):
		# para passed in would be in unicode type, tranform to str type
		path = path.encode( 'utf8' )
		value = value.encode( 'utf8' )

		user = self.getUser()
		cellAppMgrProc = user.getProc( "cellappmgr" )

		if not cellAppMgrProc:
			raise ServerStateException(	"CellAppMgr no longer exists" )

		cellAppMgrProc.setWatcherValue( path, value )

		return dict( path = path, value = value )

	# setCellAppMgrWatcher

	
	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def getCellAppMgrWatcher( self, path ):
		# para passed in would be in unicode type, tranform to str type
		path = path.encode( 'utf8' )

		user = self.getUser()
		cellAppMgrProc = user.getProc( "cellappmgr" )

		if not cellAppMgrProc:
			raise ServerStateException(	"CellAppMgr no longer exists" )

		return dict( path = path, 
					value = cellAppMgrProc.getWatcherValue( path ) )

	# getCellAppMgrWatcher


	@identity.require( Permission( 'view' ))
	@expose( "json" )
	def getLoadBalanceStatus( self ):
		user = self.getUser()
		cellAppMgrProc = user.getProc( "cellappmgr" )

		if not cellAppMgrProc:
			raise ServerStateException(	"CellAppMgr no longer exists" )

		svrLoadBalancePath = "debugging/shouldLoadBalance"
		metaLoadBalancePath = "debugging/shouldMetaLoadBalance"
		isProductionModePath = "isProduction"

		watcherPaths = [ svrLoadBalancePath,
						metaLoadBalancePath,
						isProductionModePath ]

		watcherValues = cellAppMgrProc.getWatcherValues( watcherPaths )

		if not watcherValues:
			raise ServerStateException(
						"Failed to retrieve CellAppMgr watchers" )

		return dict(
				svrLoadBalanceEnabled = watcherValues[ svrLoadBalancePath ],
				metaLoadBalanceEnabled = watcherValues[ metaLoadBalancePath ],
				isProductionMode = watcherValues[ isProductionModePath ] )

	# getLoadBalanceStatus


	#~~~~~~~~~~~~~~~~~~~~~	JSON services  ~~~~~~~~~~~~~~~~~~~~~~~~~~

	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def get_entity_types( self, space ):
		"""
		Returns the dictionary of entity types for this L{Space},
		where keys are the integer entity type id and values are
		the string entity name.
		"""
		spaceId = int( space )

		try:
			cellTalker = self.getCellApp( spaceId )
			cellTalker.getTypeNames()
			entityTypeDict = cellTalker.typeName;

			return json.dumps( entityTypeDict, indent = JSON_INDENT_SPACES )
		except Exception, ex:
			return json.dumps( ex, indent = JSON_INDENT_SPACES,
				default = serialiseObjectToJson )
	# get_entity_types


	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def get_space( self, space, cell = 0 ):
		spaceId = int( space )
		cellId = int( cell )
		try:
			return self.getSpaceDataAsJson( spaceId, cellId )
		except Exception, ex:
			return json.dumps( ex, indent = JSON_INDENT_SPACES,
				default = serialiseObjectToJson )
	# get_space


	#~~~~~~~~~~~~~~~~~~~~~~~  support methods ~~~~~~~~~~~~~~~~~~~~~~~

	def getSpaceDataAsJson( self, spaceId, cellAppID = 0 ):
		data = self.getSpaceData( spaceId, cellAppID )
		return json.dumps( data, indent = JSON_INDENT_SPACES,
			default = serialiseObjectToJson )
	# getSpaceDataAsJson


	def getSpaceData( self, spaceId, cellAppID ):

		cellAppMgr = self.getCellAppMgr( spaceId )
		selectedCell = cellAppMgr.cells.values()[0]

		for cell in cellAppMgr.cells.values():
			if cell.appID == cellAppID:
				selectedCell = cell

		cellTalker = CellTalker( cellAppMgr.space, selectedCell )

		cellTalker.getGrid()
		cellTalker.getReals()
		cellTalker.getGhosts()

		selectedCell.realEntities = cellTalker.entityData
		selectedCell.ghostEntities = cellTalker.ghostEntityData

		cellLoad = [ x.load for x in cellAppMgr.cells.values() ]
		minLoad = 999.9
		maxLoad = -1.0
		avgLoad = 0.0

		for load in cellLoad:
			if load < minLoad:
				minLoad = load
			if load > maxLoad:
				maxLoad = load
			avgLoad += load
		avgLoad /= len( cellLoad )

		return dict(
			root = cellAppMgr.root,
			stats = dict(
				cells = len( cellAppMgr.cells ),
				cellapps = cellAppMgr.appsTotal,
				minLoad = minLoad,
				maxLoad = maxLoad,
				avgLoad = avgLoad,
			),
			mappings = cellAppMgr.getSpaceGeometryMappings(),
			spaceBounds = cellTalker.spaceBounds,
			gridResolution = cellTalker.gridResolution,
			selectedCell = selectedCell.appID )
	# getSpaceData


	def querySpaces( self,
				query = None, index = None, limit = 25,
				sortby = 'id', sortdir = 'asc', **unsupported ):
		"""
		Returns space information for the current web console user
		as a tuple of (sortedFilteredSpaces, spaceIdsMatchingFilter, allSpaceIds ).
		"""
		user = self.getUser()
		cellAppMgrProc = user.getProc( "cellappmgr" )

		if not cellAppMgrProc:
			if not user.getServerProcs():
				raise Exception( "BigWorld Server is not running" )
			else:
				raise Exception( "No CellAppMgr processes running" )

		path = "spaces/*"

		# allow exceptions to propagate
		table = watcher.getFilteredTree( path, [cellAppMgrProc] )

		# list of (int) space Ids
		spaceIds = [ int( s ) for s in table.values['cellappmgr'].keys() ]

		if not spaceIds:
			log.debug( "server is up, but no spaces are loaded" )
			return ([], [], [])

		log.debug( "%d total spaces", len( spaceIds ) )

		# apply query predicates
		# only simple ID matching for now due to performance issues with
		# query watcher data for large numbers of spaces.
		filteredSpaceIds = spaceIds
		if query:
			filteredSpaceIds = []
			query = str( query )
			log.debug( "filtering spaces by: %r", query )
			for spaceId in spaceIds:
				if query == str( spaceId ):
					filteredSpaceIds.append( spaceId )

			if not filteredSpaceIds:
				log.debug( "no spaces after filtering" )
				return (filteredSpaceIds, filteredSpaceIds, spaceIds)

			log.debug( "%d spaces after filtering", len( filteredSpaceIds ) )

		# numeric sort by id
		filteredSpaceIds.sort( reverse = (sortdir == 'desc') )

		# truncate if necessary
		sortedFilteredSpaceIds = filteredSpaceIds
		try:
			index = int( index )
			if index:
				sortedFilteredSpaceIds = sortedFilteredSpaceIds[ index: ]
				log.debug( "truncated space list to start at %d", index )
		except:
			pass

		try:
			limit = int( limit )
			if limit > 0:
				sortedFilteredSpaceIds = sortedFilteredSpaceIds[ :limit ]
				log.debug( "truncated space list to %d spaces", limit )
		except:
			pass

		spacesList = []
		for spaceId in sortedFilteredSpaceIds:

			# get load info from watchers
			space = None
			path = "spaces/%d/*" % spaceId
			try:
				table = watcher.getFilteredTree( path, [cellAppMgrProc] )
				space = table.values['cellappmgr']
				del space['cells']
				for prop, value in space.items():
					space[ prop ] = value[ 0 ]

			except watcher.Error, ex:
				pass

			spacesList.append( space )

			# get space geometry for each space, so that e.g.:
			#   space['geometry'] = "spaces/highlands"
			#   space['name'] = "highlands"
			#
			# note: space['geometry'] will not be defined unless watcher
			# 'cellappmgr/spaces/<spaceId>/geometry' exists (introduced in BW 2.2)
			spaceName = space.get( 'geometry', None )
			if not spaceName is None:
				# BW version >= 2.2
				space['name'] = space['geometry'].rsplit("/", 1 )[ -1 ]
			else:
				# BW version < 2.2
				# fallback to CellAppMgrTalker.getSpaceGeometryMappings()
				cellAppMgr = self.getCellAppMgr( space['id'] )
				mappings = cellAppMgr.getSpaceGeometryMappings()
				if mappings:
					# mappings is [ geomIndex, geomTransformMatrix, geomMappingName ]
					mappings = [ x[2] for x in mappings ]
					space['geometry'] = ":".join( mappings )

					mappings = [ x.rsplit("/", 1 )[ -1 ] for x in mappings ]
					space['name'] = ":".join( mappings )
				else:
					space['geometry'] = mappings = []
					space['name'] = ''

		return (spacesList, filteredSpaceIds, spaceIds)
	# querySpaces


	def getCellAppMgr( self, spaceId ):
		"""
		Returns a L{CellAppMgrTalker} for the given space_id. Due to
		the expense of looking up a User object for every HTTP request,
		L{CellAppMgrTalker} IPs are cached between requests for a short time.
		The L{CellAppMgrTalker} returned is guaranteed to have just called
		L{CellAppMgrTalker.getCells}.
		"""

		serverUserName = util.getServerUsername()

		if CELLAPPMGR_CACHE_TTL:
			try:
				ipAddr = self.cellAppMgrCache.get( serverUserName )
				log.debug(
					"using cached cellAppMgr IP (%s:%s) for space %d, user %s",
					ipAddr[0], ipAddr[1], spaceId, serverUserName  )

				cellAppMgr = CellAppMgrTalker( space = spaceId, addr = ipAddr )

				return cellAppMgr
			except:
				# KeyError -- not in cache or expired from cache
				# socket.error -- cellAppMgr IP invalid or failed to contact
				pass

		# cache miss; lookup a fresh CellAppMgrTalker
		log.info( "looking up cellAppMgr for space %d of user %s",
				spaceId, serverUserName )

		ipAddr = self.getCellAppMgrIp()
		cellAppMgr = None
		try:
			cellAppMgr = CellAppMgrTalker( space = spaceId, addr = ipAddr )

			# getCells is called in the CellAppMgrTalker constructor but
			# check for it just in case.
			if not cellAppMgr.cells:
				cellAppMgr.getCells()
		except socket.timeout, ex:
			# handle cellAppMgr.getCells() timeout (space doesn't exist)
			log.exception( "Couldn't create CellAppMgrTalker: %s", ex )
			raise SpaceViewerException( "Space %s doesn't exist" % spaceId )

		if CELLAPPMGR_CACHE_TTL:
			self.cellAppMgrCache.put( serverUserName, ipAddr )

		return cellAppMgr
	# getCellAppMgr


	def getCellAppMgrIp( self ):
		"""
		Returns the IP address and port on which a CellAppMgr is running
		as self.userId; returns a tuple of (ip, port).
		"""

		user = self.getUser()
		cellAppMgr = user.getProc( "cellappmgr" )
		if not cellAppMgr:
			raise SpaceViewerException( "Couldn't locate a CellAppMgr" )

		port = cellAppMgr.getWatcherValue( "viewer server port" )
		if not port:
			raise ServerStateException(
				"CellAppMgr is running but viewer server port watcher is unset" )

		port = int( port )
		ip_port = ( cellAppMgr.machine.ip, port )
		log.info("found cellappmgr for user '%s' at %s:%s"
			, user, ip_port[0], ip_port[1] )

		return ip_port
	# getCellAppMgrIp


	def getCellApp( self, spaceId, cellId=None ):
		"""
		Returns the L{CellTalker} (cell) for the given space and cell id,
		or returns None if no cellapp can be found for the given space
		and cell id (ie: "cell appID").

		If cellId is not given (or is boolean False), this method will
		return the least-loaded CellApp that is currently handling the
		given spaceId.
		"""
		if not cellId:
			cellId = self.getCellAppIdsForSpace( spaceId )[0]
			return self.getCellApp( spaceId, cellId )

		cellAppMgr = self.getCellAppMgr( spaceId )
		for cell in cellAppMgr.cells.values():
			if cell.appID == cellId:
				break

		if not cell:
			raise SpaceViewerException(
				"No cellapp for space %s with appID '%s'" % ( spaceId, cellId ) )

		ct = CellTalker( spaceId, cell )
		log.info( "found cellapp with id %s for space %s at %s"
				, cellId, spaceId, ct.getInetAddress() )

		return ct
	# getCellApp


	def getCellAppIdsForSpace( self, spaceId ):
		"""
		Returns a list of cell ids that are currently handling the
		given spaceId.
		"""
		user = self.getUser()
		cellAppMgrProc = user.getProc( "cellappmgr" )
		path = "spaces/%s/cells" % spaceId
		cappWatcherData = cellAppMgrProc.getWatcherData( path ).getChildren()

		# get list of cellApp watchers
		cellApps = [ x.getChild("app") for x in cappWatcherData ]
		if not cellApps:
			raise SpaceViewerException(
				"There are no cellapps for spaceId '%s'" % spaceId )

		# put lowest loaded cellapp first in the list
		# this is for the case where client code needs info from a CellApp
		# and any single CellApp will do.
		if len( cellApps ) > 1:
			minLoad = 999
			for i in range( len( cellApps ) ):
				load = cellApps[i].getChild( "load" ).value
				if load < minLoad:
					minLoad = load
					minLoadIndex = i
			cellApps[0], cellApps[i] = cellApps[i], cellApps[0]

		cellAppIds = [ cellapp.getChild("id").value for cellapp in cellApps ]

		log.info("CellApps currently handling space %s: %s"
				, spaceId, cellAppIds )

		return cellAppIds
	# getCellAppIdsForSpace


	def getUser( self ):
		return util.getUser( cluster.cache.get() )
	# getUser


	def _initServiceAppCache( self ):
		"""
		Populate cache of serviceapps running HTTPResTreeService from the current
		server state, discarding old cached entries.
		"""
		user = self.getUser()
		serviceAppProcList = user.getProcs( "serviceapp" )

		watcherPath = "services/data/space_viewer_http"
		try:
			table = watcher.getFilteredTree( watcherPath, serviceAppProcList )
		except watcher.Error, ex:
			log.warning( "Watcher error for path '%s': %s", watcherPath, ex )
			return None

		serverUserName = util.getServerUsername()
		ipList = [item[0] for item in table.values.values() if item[0]]

		if not ipList:
			log.warning( "No serviceapps running spaceviewer resource service (%s)",
					serverUserName )
			return None

		log.info( "Serviceapps running spaceviewer resource service (%s): %r",
				serverUserName, ipList )

		self.tileServiceAppCache = TimedCache( ttl = TILE_CACHE_TTL )
		self.tileServiceAppCache.put( serverUserName, ipList )
		self._lastServiceAppCacheIndex = 0

		return ipList
	# _initServiceAppCache


	def _removeFromServiceAppCache( self, ipAddress ):
		""" Clears the current server user's serviceapp IP cache. Returns True
			if the cache was cleared or False if cache was already empty. """

		serverUserName = util.getServerUsername()
		serviceAppIpList = self.tileServiceAppCache.get( serverUserName )

		if not serviceAppIpList:
			return False

		# just remove them all to force a re-init
		self.tileServiceAppCache.put( serverUserName, [] )
		return True

	# _removeFromServiceAppCache


	def getNextTileServiceIp( self ):

		# tileServiceAppCache will not be defined the first time this method
		# is called. Deferred init is required because cache must be initialised
		# within the scope of a HTTP request (to get current server username).
		if not hasattr( self, 'tileServiceAppCache' ):
			if not self._initServiceAppCache():
				return None

		serverUserName = util.getServerUsername()
		serviceAppIpList = self.tileServiceAppCache.get( serverUserName )

		# if no serviceapps cached, try to re-init cache from broadcast
		if not serviceAppIpList:
			serviceAppIpList = self._initServiceAppCache()
			if not serviceAppIpList:
				return None

		self._lastServiceAppCacheIndex += 1

		if self._lastServiceAppCacheIndex >= len( serviceAppIpList ):
			self._lastServiceAppCacheIndex = 0

		return serviceAppIpList[ self._lastServiceAppCacheIndex ]
	# getNextTileServiceIp

# end of class SpaceViewerController

# controllers.py

