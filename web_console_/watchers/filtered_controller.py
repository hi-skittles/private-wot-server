import turbogears
import sqlobject

from turbogears.controllers import expose
from turbogears import identity

from pycommon import cluster

from web_console.common import ajax
from web_console.common import util

from pycommon import watcher_tree_filter
from pycommon import command_util

import model as watcher_model

import preconfigured


class FilteredController( turbogears.controllers.Controller ):


	def __init__( self ):
		turbogears.controllers.Controller.__init__( self )


	@identity.require( identity.not_anonymous() )
	@expose( template="watchers.templates.filtered" )
	def index( self, processes = "", path = "" ):
		return dict( processes = processes, path = path )


	# Returns a string on error
	def _getFilteredTree( self, processes, path ):
		c = cluster.cache.get()

		# TODO: Make this a configuarable user.
		user = util.getUser( c, None )
		clusterProcs = command_util.selectProcesses( user, [processes] )

		if not clusterProcs:
			# TODO: Check that the server is running
			return "No processes matching '%s'" % processes

		try:
			tree = watcher_tree_filter.getFilteredTree( str( path ), clusterProcs )
		except watcher_tree_filter.Error, e:
			return e.msg

		return tree


	@identity.require( identity.not_anonymous() )
	@expose( template="common.templates.error" )
	def csv( self, processes, path, filename = None ):
		tree = self._getFilteredTree( processes, path )

		if isinstance( tree, (str, unicode) ):
			return util.getErrorTemplateArguments(
				message = tree,
				error = "Invalid filter request",
			)

		import StringIO
		outString = StringIO.StringIO()
		tree.write( outString )

		if filename is None:
			filename = "attachment; filename=" + processes + '_' + \
				path.replace( '/', '_' ).replace( '*', 'X' ) + ".csv"

		import cherrypy
		cherrypy.response.headers[ "Content-type" ] = "text/csv"
		cherrypy.response.headers[ "Content-Disposition" ] = \
			"attachment; filename=" + filename
		return outString.getvalue()


	@identity.require( identity.not_anonymous() )
	@turbogears.expose( format = "json" )
	def get_filtered_tree( self, processes, path ):
		tree = self._getFilteredTree( processes, path )

		if isinstance( tree, basestring ):
			return dict( status = False, errorMsg = tree )

		return dict( tree=tree, status=True,
				processes=processes, path=path )


	@identity.require( identity.not_anonymous() )
	@turbogears.expose( format = "json" )
	def get_saved_filters( self ):

		uid = util.getSessionUID()
		userFilters = list( watcher_model.watcherFilters.select(
							watcher_model.watcherFilters.q.userID == uid ) )
		userFilters.sort( lambda x, y : cmp( x.name, y.name ) )

		return dict( globalFilters = preconfigured.WATCHER_FILTERS,
				userFilters = userFilters )


	@identity.require( identity.not_anonymous() )
	@turbogears.expose( format = "json" )
	def save_new_filter( self, name, processes, path ):

		name = str( name )
		processes = str( processes )
		path = str( path )

		status = True

		# Check global filters for the same name
		if preconfigured.hasWatcherFilter( name ):
			status = False
			message = "A global filter of the same name already exists."

		if status:
			# check user filters for the same name
			uid = util.getSessionUID()
			userFilters = list( watcher_model.watcherFilters.select(
							sqlobject.AND(
								watcher_model.watcherFilters.q.userID == uid,
								watcher_model.watcherFilters.q.name == name )))

			if userFilters:
				status = False
				message = "A custom user filter of the same name already exists."


		if status:
			user = util.getSessionUser()
			newFilter = watcher_model.watcherFilters( user = user, name = name,
								processes = processes, path = path )
			print "new filter:", newFilter
			message = "'%s' saved successfully" % name


		return dict( status = status, message = message )


	@identity.require( identity.not_anonymous() )
	@turbogears.expose( format = "json" )
	def delete_filter( self, name ):
		# check user filters for the same name
		uid = util.getSessionUID()
		userFilters = list( watcher_model.watcherFilters.select(
						sqlobject.AND(
							watcher_model.watcherFilters.q.userID == uid,
							watcher_model.watcherFilters.q.name == name )))

		status = True
		message = ""
		if not userFilters:
			status = False
			message = "No custom filter '%s' available for deletion" % name

		else:
			watcher_model.watcherFilters.delete( userFilters[ 0 ].id )

		return dict( status = status, message = message )

# filtered_controller.py
