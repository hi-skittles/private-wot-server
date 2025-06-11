import cherrypy
import turbogears

from turbogears import controllers, expose, redirect
from turbogears import identity

from pycommon import uid as uid_module
from web_console.common import model, module, util
from web_console.common.authorisation import Permission

# Local modules
import utils
import graph
import managedb
import socket

class StatGrapher( module.Module ):

	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )
		utils.setup()

		self.graph = graph.StatGrapherBackend()
		managedb.setup( self.graph.prefsRequester.prefFileName, 
				self.graph.prefsRequester.retrieveOptions() )

		self.addPage( "Processes", "latestUserProcesses" )
		self.addPage( "Machines", "latestMachines" )
		self.addPage( "Users", "allUsers" )
		self.addPage( "Archive", "list" )
		self.addPage( "Help", "help" )
	# __init__


	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self ):
		raise turbogears.redirect( "latestUserProcesses" )
	# index


	@identity.require( Permission( 'view' ) )
	@expose()
	def latestUserProcesses( self, **kwargs ):
		userServerName = util.getServerUsername()
		uid = uid_module.getuid( userServerName )

		maxLogDb = self.getLatestUpdatedLog()
		return self.graph.processes( maxLogDb, uid, **kwargs )
	# latestUserProcesses


	@identity.require( Permission( 'view' ) )
	@expose()
	def latestMachines( self, **kwargs ):
		maxLogDb = self.getLatestUpdatedLog()
		return self.graph.machines( maxLogDb, **kwargs )
	# latestMachines


	@identity.require( Permission( 'view' ) )
	@expose( template = "stat_grapher.templates.listusers" )
	def allUsers( self ):
		maxLogDb = self.getLatestUpdatedLog()
		created, used, active, users = \
			managedb.getRawDbManager()._getInfoAboutLogDb( maxLogDb )

		action = turbogears.url("statg/graph/processes")

		# List of users
		users.sort( lambda x, y: cmp( x[1], y[1] ) )

		return dict( outputList = users,
			action = action,
			log = maxLogDb,
			pageHeader="List of users in log database %s" % (maxLogDb) )
	# allUsers


	def getLatestUpdatedLog( self ):
		# find the log database that has been updated the latest
		list = managedb.getRawDbManager().getLogDbList()
		if not list:
			raise redirect( "list" )
		maxLogDb = None
		maxUsed = None
		for name, created, used, active, user in list:
			if maxUsed == None or maxUsed < used:
				maxUsed = used
				maxLogDb = name
		return maxLogDb
	# getLatestUpdatedLog


	@identity.require( Permission( 'view' ) )
	@expose( template = "stat_grapher.templates.listlogs" )
	def list( self ):
		list = managedb.getRawDbManager().getLogDbList()
		# List of databases
		outputList = []
		for name, created, used, active, user in list:
			# List of actions
			actions = util.ActionMenuOptions()
			actions.addRedirect( "View machine graphs",
				"../statg/graph/machines/%s" % name,
				help="View a graph of machines recorded " \
					"in \"%s\"" % (name) )
			actions.addRedirect( "View process graphs",
				"../statg/listUsers/%s" % name,
				help="View a graph of a user's processes recorded " \
					"in \"%s\"" % (name) )

			actions.addRedirect( "View preferences",
				"../statg/prefs/%s" % name,
				help="View a list of a preferences used " \
					"in \"%s\"" % (name) )

			outputList.append( (name, created, used, active, actions) )

		return dict( outputList = outputList )
	# list


	@identity.require( Permission( 'view' ) )
	@expose( template = "stat_grapher.templates.listusers" )
	def listUsers(self, log):
		created, used, active, users = \
			managedb.getRawDbManager()._getInfoAboutLogDb( log )

		# List of users
		action = turbogears.url("statg/graph/processes")

		# sort by name
		users.sort( lambda x, y: cmp( x[1], y[1] ) )
		return dict( outputList = users,
			action = action,
			log = log,
			pageHeader="List of users in log database %s" % (log) )
	# listUsers


	@identity.require( Permission( 'view' ) )
	@expose( template = "stat_grapher.templates.prefs" )
	def prefs(self, log):
		_, prefTree = managedb.ptManager.requestDbManager( log )
		displayPrefs = self.graph.requestDisplayPrefs( log )

		return dict(
			prefTree = prefTree,
			displayPrefs = displayPrefs,
			log = log,
			pageHeader="Preferences used in log database %s" % (log) )
	# prefs

# end class StatGrapher

# controllers.py
