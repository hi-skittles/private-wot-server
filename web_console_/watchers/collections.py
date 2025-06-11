import logging
import sqlobject
import turbogears
from turbogears import expose
from turbogears import identity

from pycommon import cluster
from web_console.common import ajax
from web_console.common import util
from web_console.cluster_control import model as cluster_model
from web_console.common.authorisation import Permission

log = logging.getLogger( __name__ )


def getCollections( userid = None ):
	if userid == None:
		userid = util.getSessionUID()

	# Obtain the current users list of watcher collections
	try:
		customList = list( cluster_model.ccCustomWatchers.select(
			cluster_model.ccCustomWatchers.q.userID == userid ))
	except:
		customList = []

	return customList


# Return the requested watcher collection for the current
# sessions user or if provided an alternate user.
def getCollection( name, userid=None ):
	if userid == None:
		userid = util.getSessionUID()

	collection = list( cluster_model.ccCustomWatchers.select(
				sqlobject.AND(
					cluster_model.ccCustomWatchers.q.userID == userid,
					cluster_model.ccCustomWatchers.q.pageName == name ) ))
	return collection[0]


class Collections( turbogears.controllers.Controller ):

	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self ):
		raise turbogears.redirect( turbogears.url( "list" ) )



	# Display the contents of a watcher collection
	@identity.require( Permission( 'view' ) )
	@expose( template = "web_console.watchers.templates.collection" )
	@util.unicodeToStr
	def view( self, name=None ):

		if not name:
			raise Exception( "No watcher collection name provided." )

		try:
			collection = getCollection( name )
		except:
			return Exception( "No watcher collection '%s' known." % name )

		try:
			recs = list( cluster_model.ccCustomWatcherEntries.select(
						 cluster_model.ccCustomWatcherEntries.q.customWatcherPageID ==
							collection.id ))
		except Exception, e:
			recs = []
			msg = "No watchers in this collection"

		# If there are no watcher path entries for this collection (which could
		# occur through reloading the collection after deleting the final
		# watcher path), redirect back to the list of watcher collections pages.
		if not len(recs):
			raise turbogears.redirect( turbogears.url( "list" ) )

		# Store the watchers / components
		queryDict = {}
		for rec in recs:
			if not queryDict.has_key( rec.componentName ):
				queryDict[ rec.componentName ] = []

			queryDict[ rec.componentName ].append( rec.watcherPath )


		# The cluster / process information we need to
		# query for our watcher layouts
		c = cluster.cache.get()
		user = util.getUser( c )
		procs = user.getServerProcs()

		# Each component has a list inserted into a dict containing:
		# ( [watchers, ... ],
		#   { 'component': [ val, ... ], ... }
		# )
		#
		# eg:
		# ( [ 'load', 'gameTime', ... ],
		#   { 'cellapp01': [ '0.0140622', '0.24834', '0.8734552' ],
		#     'cellapp02': [ '0.0140622', '0.24834', '0.8734552' ] }
		# )

		# NB: Potential change for this structure to provide a
		#     more flexible user based option display in the template.
		#
		#
		# ( [ 'load', 'gameTime', ... ],
		#   [ 'cellapp01', 'cellapp02', ... ],
		#   [
		#       ['0.0140622', '0.24834', ... ],
		#       ['0.24834', '0.8734552', ... ],
		#       ...
		#   ]
		# )

		finalResults = {}

		for i in procs:

			if not queryDict.has_key( i.name ):
				continue

			if not finalResults.has_key( i.name ):
				finalResults[ i.name ] = (queryDict[ i.name ], {})


			# Remember the process label so we can display it
			pname = i.label()

			# Insert the current process into the list of all processes
			# of the same component type
			if not finalResults[ i.name ][1].has_key( pname ):
				finalResults[ i.name ][1][ pname ] = []

			vlist = queryDict[ i.name ]

			for strPath in vlist:

				# TODO: when types are implemented for the watcher
				#       add the type as a 3rd field
				tmpres = i.getWatcherValue( strPath )

				# If the value returned by the Watcher happens to be None
				# the process will be set to mute, so we need to force
				# it back for any subsequent requests to work.
				i.mute = False

				tmp = ( strPath, tmpres )

				finalResults[ i.name ][1][ pname ].append( tmpres )

		return dict( results=finalResults, name=name )


	# Called by static/js/collections.js: deleteCollection()
	@identity.require(identity.not_anonymous())
	@ajax.expose
	def deleteCollection( self, collection ):

		try:
			collectionObj = getCollection( collection )
			# Due to the table definitions, destroying this object will
			# cascade row deletions into the cc_custom_watcher_entries table
			collectionObj.destroySelf()
		except Exception, e:
			log.error( "Exception while searching for watcher collection entry" )
			log.error( str(e) )

			return "Unable to find the requested watcher collection to delete"

		return "Watcher collection %s deleted" % collection


	# Display a list of watcher collections for the current user
	@identity.require( Permission( 'view' ) )
	@expose( template="web_console.watchers.templates.collections" )
	def list( self ):
		c = cluster.cache.get()
		user = util.getUser( c )

		collectionsList = getCollections()
		collections = []

		# Generate the list of watchers and associated menu items
		for collection in collectionsList:

			try:
				entryObj = cluster_model.ccCustomWatcherEntries.select( sqlobject.AND(
					cluster_model.ccCustomWatcherEntries.q.customWatcherPageID ==
					collection.id ) )
				count = len(list(entryObj))
			except Exception, e:
				log.error( "Trying to determine number of collection entries: %s",
							str(e) )
				count = 0

			menu = util.ActionMenuOptions()
			menu.addScript( "Delete",
				# NB: The comma after 'collection.name' is required so
				#     that the variable is passed through to the
				#     javascript function correctly.
				args = ( collection.pageName, ),
				script = "deleteCollection" )

			collections.append( (collection, menu, count) )

		return dict( collections=collections, user=user )


	# Called by static/js/collections.js: addToCollection()
	#
	# Used to save a specific component/watcher pair into a watcher collection.
	@identity.require( identity.not_anonymous() )
	@ajax.expose
	def addToCollection( self, collection, component, watcher ):
		try:
			collectionObj = getCollection( collection )
		except Exception, e:
			return "Error encountered while adding watcher to watcher collection.\n%s" % str( e )

		try:
			cluster_model.ccCustomWatcherEntries( customWatcherPage = collectionObj,
									componentName = component,
									watcherPath = watcher )
		except:
			return "'%s' already saved to watcher collection '%s'" % ( watcher, collection )

		return "'%s' added to %s." % ( watcher, collection )


	# Called by static/js/collections.js: createCollection()
	# to create a new watcher collection for a user
	@identity.require( identity.not_anonymous() )
	@ajax.expose
	def createCollection( self, name ):
		c = cluster.cache.get()
		user = util.getUser( c )

		cluster_model.ccCustomWatchers(
			user = util.getSessionUID(), pageName = name )

		return "Watcher collection successfully created"


	# Called by static/js/collections.js: deleteFromCollection()
	# Delete a single watcher path associated to a component/page
	@identity.require( identity.not_anonymous() )
	@ajax.expose
	@util.unicodeToStr
	def deleteFromCollection( self, collection, component, watcherPath ):

		# Find the user
		# find the collection
		try:
			collectionObj = getCollection( collection )
		except:
			return "Failed to find watcher collection '%s'" % collection

		try:
			entries = list(cluster_model.ccCustomWatcherEntries.select(
			sqlobject.AND(
				cluster_model.ccCustomWatcherEntries.q.customWatcherPageID == collectionObj.id,
				cluster_model.ccCustomWatcherEntries.q.componentName == component,
				cluster_model.ccCustomWatcherEntries.q.watcherPath == watcherPath )))

			for i in entries:
				i.destroySelf()
		except:
			return "Failed to locate and destroy entry for '%s'" % watcherPath

		return "Watcher path removed"

# collections.py
