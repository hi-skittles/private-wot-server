import logging
import cherrypy
import turbogears
import sqlobject

from turbogears import controllers, expose, redirect, config
from turbogears import validate, validators, identity
from turbogears import widgets
from turbojson import jsonify

# Standard python modules
from StringIO import StringIO
import os
import re
import random
import threading
import traceback
import signal as sigmodule

# BigWorld modules
import bwsetup; bwsetup.addPath( "../.." )
from pycommon import cluster
from pycommon import user as user_module
from pycommon import process as process_module
from pycommon import uid as uidmodule
from pycommon import async_task
from pycommon.exceptions import AuthorisationException, ServerStateException

import pycommon.util

from web_console.common import util
from web_console.common import module
from web_console.common import ajax
from web_console.common import model as common_model
from web_console.common.authorisation import Permission

import model

# For tradeshows always ignore layout errors
#showLayoutErrors = turbogears.config.get( "server.environment" ) == "development"
showLayoutErrors = True

log = logging.getLogger( __name__ )


class ClusterControl( module.Module ):

	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )
		self.addPage( "Processes", "procs" )
		self.addPage( "Users", "users" )
		self.addPage( "Machines", "machines" )
		self.addPage( "Layouts", "layouts" )
		self.addPage( "Databases", "databases" )
		self.addPage( "Help", "help" )
		self._lock = threading.RLock()
	# __init__


	@identity.require( identity.not_anonymous() )
	@expose()
	@expose( "json", as_format="json" )
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
			log.warn( "class %s has no api method '%s'", self.__class__, methodName )
			if config.get( 'server.environment' ) == 'development':
				return { 'error': "No method '%s'" % methodName }
			else:
				raise cherrypy.HTTPError( 403 ) # forbidden
	# api


	def appendToLayout( self, layout, tag ):
		for i in xrange( len( layout ) ):
			layout[i] = layout[i] + ( tag,)
	# appendToLayout


	@identity.require( Permission( 'view', 'modify' ) )
	@expose( template="cluster_control.templates.databases" )
	def databases( self ):

		c = cluster.cache.get()
		user = util.getUser( c )
		dbapp = user.getProc( 'dbapp' )
		if dbapp:
			return self.error( "Secondary database tools cannot be accessed "
				"while DBApp is running" )

		machines = self._filterDBAppAccessibleMachines( c.getMachines() )
		machines.sort( key = lambda m: m.name )
		return { 'machines': machines }
	# databases


	@identity.require( Permission( 'modify' ) )
	@expose( "json" )
	def clearSecondaryDatabases( self, machine=None ):
		""" Runs consolidate_db with the --clear option, discarding secondary
			database changes """
		return self.consolidateSecondaryDatabases( machine = machine, discard = True );
	# clearSecondaryDatabases


	def _filterDBAppAccessibleMachines( self, machines ):
		""" Returns a list of L{Machine}s that are configured to be able to run
			the DBApp component. """

		c = cluster.cache.get()
		c.queryTags( cat = "Components", machines = machines )
		machines = filter( lambda machine: machine.canRun( 'dbapp' ), machines )

		return machines
	# _filterDBAppAccessibleMachines


	def _getMachine( self, machineName = None ):
		c = cluster.cache.get()
		machines = c.getMachines()

		# validate machine exists
		if machineName:
			for m in machines:
				if machineName == m.name or machineName == m.ip:
					return m

			raise Exception( "Unknown machine '%s'" % machine )

		# inspect WC configuration for a specific machine name
		machineName = config.get(
			'web_console.cluster.consolidate_dbs.prefered_machine', None )

		if machineName:
			for m in machines:
				if machineName == m.name or machineName == m.ip:
					return m

			raise Exception( "Unknown machine '%s'" % preferredHost )

		# otherwise, select one using heuristics
		machines = self._filterDBAppAccessibleMachines( machines )
		return random.choice( machines )
	# _getMachine


	@identity.require( Permission( 'modify' ) )
	@expose( "json" )
	def consolidateSecondaryDatabases( self, machine = None, discard = False ):
		""" Runs consolidate_db """

		c = cluster.cache.get()

		# consolidate_dbs will not run if dbapp is running
		user = util.getUser( c )
		dbapp = user.getProc( 'dbapp' )
		if dbapp:
			log.warning( "Can't consolidate_dbs while dbapp is running" )
			raise ServerStateException(
				"Can't consolidate_dbs while dbapp is running" )

		machine = self._getMachine( machine )
		assert machine
		assert machine.name

		if discard:
			log.info(
				"attempting to run consolidate_dbs --clear on machine '%s'",
				machine.name )
			pid = machine.startProcWithArgs(
				'commands/consolidate_dbs', args = ['--clear'], uid = user.uid )
		else:
			log.info(
				"attempting to run consolidate_dbs on machine '%s'",
				machine.name )
			pid = machine.startProcWithArgs(
				'commands/consolidate_dbs', args = [], uid = user.uid )

		if not pid:
			log.warning( "Couldn't start consolidate_dbs" )
			raise Exception(
				"Couldn't start consolidate_dbs on machine '%s'" % machine.name )

		log.info(
			"Started consolidate_dbs on machine '%s' (pid %d)", machine.name, pid )

		return {
			'hostname': machine.name,
			'pid': pid,
		}
	# consolidateSecondaryDatabases


	@identity.require( Permission( 'modify' ) )
	@expose( "json" )
	def clearAutoloadedEntities( self, machine = None ):
		""" Runs clear_auto_load """

		c = cluster.cache.get()

		# clear_auto_load will not run if dbapp is running
		user = util.getUser( c )
		dbapp = user.getProc( 'dbapp' )
		if dbapp:
			log.warning( "Can't clear_auto_load while dbapp is running" )
			raise ServerStateException(
				"Can't clear_auto_load while dbapp is running" )

		machine = self._getMachine( machine )
		assert machine
		assert machine.name

		log.info(
			"attempting to run clear_auto_load on machine '%s'",
			machine.name )
		pid = machine.startProcWithArgs(
			'commands/clear_auto_load', args = [], uid = user.uid )

		if not pid:
			log.warning( "Couldn't start clear_auto_load" )
			raise Exception(
				"Couldn't start clear_auto_load on machine '%s'" % machine.name )

		log.info(
			"Started clear_auto_load on machine '%s' (pid %d)", machine.name, pid )

		return {
			'hostname': machine.name,
			'pid': pid,
		}
	# clearAutoloadedEntities


	@identity.require( Permission( 'modify' ) )
	@expose( "json" )
	def syncEntityDefs( self, machine = None ):
		""" Runs sync_db """

		c = cluster.cache.get()

		# sync_db will not run if dbapp is running
		user = util.getUser( c )
		dbapp = user.getProc( 'dbapp' )
		if dbapp:
			log.warning( "Can't sync_db while dbapp is running" )
			raise ServerStateException( "Can't sync_db while dbapp is running" )

		machine = self._getMachine( machine )
		assert machine
		assert machine.name

		log.info( "attempting to run sync_db on machine '%s'", machine.name )
		pid = machine.startProcWithArgs(
			'commands/sync_db', args = '', uid = user.uid )

		if not pid:
			log.warning( "Couldn't start sync_db" )
			raise Exception(
				"Couldn't start sync_db on machine '%s'" % machine.name )

		log.info(
			"Started sync_db on machine '%s' (pid %d)", machine.name, pid )

		return {
			'hostname': machine.name,
			'pid': pid,
		}
	# syncEntityDefs


	@identity.require( Permission( 'view' ) )
	@expose( template="cluster_control.templates.procs" )
	def procs( self ):
		return {}
	# procs


	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def getProcs( self, machine = None ):
		"""
		This produces the (dict that is rendered as) JSON that is consumed
		by the 'cluster_control.templates.procs', and
		'cluster_control.templates.machine' templates.

		If a machine argument is provided, this method returns
		processes for that machine only, else returns processes for
		the current server user as given by L{util.getUser}.
		"""

		@expose( "json" )
		def return_json( input_dict ):
			return input_dict

		c = cluster.cache.get()

		if machine:
			machineObj = c.getMachine( machine )
			if not machineObj:
				raise ServerStateException(
					"Machine '%s' appears to be offline" % machine )

			# given machine may be running others' procs, so need to filter
			# proc list if current user does not have "view-other" permissions
			authEnabled = config.get( 'web_console.authorisation.on', False )
			wcUser = util.getSessionUser()
			if authEnabled and not wcUser.hasOtherPermissions( 'view' ):
				uid = c.getUser( wcUser.serveruser ).uid
				procs = machineObj.getProcs( uid = uid )
			else:
				procs = machineObj.getProcs()

			dict = {
				'procs': procs,
				'machine': machineObj,
				'isServerRunning': True,
			}
		else:
			user = util.getUser( c, fetchVersion = True )
			procs = user.getProcs()

			missingProcs = set()
			serverProcs = user.getServerProcs()

			if serverProcs:
				user.serverIsRunning( missingProcs )

			if missingProcs:
				missingProcs = tuple( missingProcs )
			else:
				missingProcs = None

			layoutErrors = None
			if showLayoutErrors:
				layoutErrors = user.getLayoutErrors()

			dict = {
				'procs': procs,
				'user': user,
				'layoutErrors': layoutErrors,
				'isServerRunning': (len( serverProcs ) > 0),
				'missingProcessTypes': missingProcs
			}

		# if more than one thread is using the expose to convert the dictionary
		# to JSON, it may cause the NoApplicableMethods exception, so add the
		# lock to only allow one thread one time to expose the JSON format
		try:
			self._lock.acquire()
			json_list = return_json( dict )
		finally:
			self._lock.release()

		return json_list
	# procs


	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self ):
		raise redirect( turbogears.url( "procs" ) )
	# index


	@identity.require( Permission( 'view' ) )
	@expose( template="cluster_control.templates.machine" )
	def machine( self, machine ):
		return { 'machine': machine }
	# machine


	@identity.require( Permission( 'view' ) )
	@expose( template="cluster_control.templates.machines" )
	def machines( self, **kwargs ):
		return kwargs
	# machines



	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def getMachines( self, tags = False ):
		"""
		This produces the (dict that is rendered as) JSON that is consumed
		by the 'cluster_control.templates.machines' template.
		"""
		c = cluster.cache.get( shouldRetrievePlatformInfo = True )
		machines = c.getMachines()

		if config.get( 'web_console.authorisation.on', False ):
			user = util.getSessionUser()
			if not user.hasOtherPermissions( 'view' ):
				uid = c.getUser( user.serveruser ).uid
				assert uid
				machines = filter( lambda m: m.getProcs( uid = uid ), machines )

		if tags:
			c.queryTags( cat = "Components", machines = machines )
			c.queryTags( cat = "Groups", machines = machines )

		return dict( ms = machines )
	# getMachines


	@identity.require( Permission( 'view' ) )
	@expose( template="cluster_control.templates.users" )
	def users( self, **kwargs ):
		return kwargs
	# users


	@identity.require( Permission( 'view' ) )
	@expose( "json" )
	def getUsers( self, inactive = False ):

		@expose( "json" )
		def return_json( input_dict ):
			return input_dict

		c = cluster.cache.get()

		if config.get( 'web_console.authorisation.on', False ):
			wcUser = util.getSessionUser()
			if not wcUser.hasOtherPermissions( 'view' ):
				user = util.getUser( c, wcUser.serveruser )
				user.procs = user.getProcs()
				user.isActive = True
				return_dict = { 'users': [ user ] }

				# if more than one thread is using the expose to convert the
				# dictionary to JSON, it may cause the NoApplicableMethods
				# exception, so add thelock to only allow one thread one time to
				# expose the JSON format
				try:
					self._lock.acquire()
					json_list = return_json( return_dict )
				finally:
					self._lock.release()

				return json_list

		activeUsers = c.getUsers()

		users = {}
		for user in uidmodule.getall():
			users[ user.name ] = user
			user.procs = user.getProcs()
			user.isActive = False

		for user in activeUsers:
			if user.name in users:
				users[ user.name ].isActive = True

		if not inactive:
			users = dict( [ (u.name, u) for u in users.values() if u.isActive ] )

		return_dict = { 'users': users.values() }

		# if more than one thread is using the expose to convert the dictionary
		# to JSON, it may cause the NoApplicableMethods exception, so add the
		# lock to only allow one thread one time to expose the JSON format
		try:
			self._lock.acquire()
			json_list = return_json( return_dict )
		finally:
			self._lock.release()

		return json_list
	# getUsers


	# Perform the same functionality as the control_cluster 'flush' command.
	# This should only be called from the "All Users" page, and then return
	# the user to that page with an updated user list.
	@identity.require( identity.not_anonymous() )
	@expose()
	def usersFlush( self ):

		c = cluster.cache.get()
		ms = c.getMachines()

		for m in ms:
			m.flushMappings()

		raise redirect( "users" )
	# usersFlush


	@identity.require( Permission( 'modify' ) )
	@expose( template="cluster_control.templates.start" )
	def start( self ):

		user = util.getServerUsername()
		c = cluster.cache.get()
		try:
			user = c.getUser( user, refreshEnv = True, checkCoreDumps = True,
						fetchVersion = True )
		except Exception, e:
			raise redirect( "/error", message = str( e ) )

		try:
			prefs = model.ccStartPrefs.select(
				model.ccStartPrefs.q.userID == util.getSessionUID() )[0]
		except:
			prefs = model.ccStartPrefs( user = util.getSessionUser(),
										last_mode = "single",
										last_machine = "",
										last_layout = "",
										last_group = "",
										useTags = True )

		# It is possible that last_machine, last_layout and last_group contain
		# a value of NULL from starting a cluster by group name and selecting
		# '(use all machines)' or from automatically creating a field using
		# VERIFY_COLS. If this occurs we must force these fields to be an empty
		# string so the KID template doesn't fail.
		if prefs.last_machine == None:
			prefs.last_machine = ""
		if prefs.last_layout == None:
			prefs.last_layout = ""
		if prefs.last_group == None:
			prefs.last_group = ""

		savedLayouts = model.ccSavedLayouts.select(
			model.ccSavedLayouts.q.userID == util.getSessionUID() )

		return dict( user = user, c = c, prefs = prefs,
					 savedLayouts = [x.name for x in savedLayouts] )
	# start


	@identity.require( Permission( 'modify' ) )
	@expose( template="cluster_control.templates.startproc" )
	@validate( validators = dict( count=validators.Int() ) )
	def startproc( self, pname=None, machine=None, count=None ):

		c = cluster.cache.get()
		user = util.getUser( c )

		# Ensure the count is correctly set for the singletons.
		# This is important because the field isn't passed through when
		# the input field is disabled.
		if pname and process_module.Process.types[pname].meta.isSingleton:
			count = 1

		# We're actually starting the processes
		if pname and machine and count:

			m = c.getMachine( machine )

			# Start the processes
			pname = pname.encode( "ascii" )
			user.startProc( m, pname, count )

			# Set this is as the default for next time
			for rec in model.ccStartProcPrefs.select(
				model.ccStartProcPrefs.q.userID == util.getSessionUID() ):
				rec.destroySelf()

			model.ccStartProcPrefs(
				user = util.getSessionUser(),
				proc = pname,
				machine = machine,
				count = count )

			raise redirect( "procs" )

		# We're displaying the page to select what to start
		else:

			machines = sorted( c.getMachines(), key = lambda x: x.name )

			try:
				prefs = model.ccStartProcPrefs.select(
					model.ccStartProcPrefs.q.userID == util.getSessionUID() )[0]

			except IndexError:
				prefs = model.ccStartProcPrefs( user = util.getSessionUser() )

			# Generate a tuple of value and presentation information for the
			# selection list in the start procs page.
			machineList = []
			for m in machines:
				machineList.append( ( m.name,
					m.name + "  - (" + str( m.ncpus ) + " cpu )" ) )
			
			startableProcesses = list( process_module.Process.types.startable( 
				version = user.version ).keys() )
			startableProcesses.sort( process_module.Process.cmpByName )

			procList = [ ( p, p ) for p in startableProcesses]

			return dict( user = user, machines = machineList, prefs = prefs,
						proclist = procList )
	# startproc


	@identity.require( Permission( 'modify' ) )
	@expose()
	@validate( validators = dict( pid = validators.Int() ) )
	def stopproc( self, machine, pid ):

		c = cluster.cache.get()
		m = c.getMachine( machine )
		p = m.getProc( pid )
		u = p.user()

		if util.getServerUsername() != u.name:
			raise AuthorisationException( "Permission denied" )

		p.stopNicely()

		raise redirect( "procs" )
	# stopproc


	@identity.require( Permission( 'modify' ) )
	@expose()
	@validate( validators = dict( pid = validators.Int(),
								  signal = validators.Int(),
								  restart = validators.StringBool() ) )
	def killproc( self, machine, pid, signal, restart = False ):

		c = cluster.cache.get()
		m = c.getMachine( machine )
		p = m.getProc( pid )
		
		if not p:
			raise ServerStateException(
				"No process with machine '%s' and PID '%d'" % ( machine, pid ) )
				
		u = p.user()

		if util.getServerUsername() != u.name:
			raise AuthorisationException( "Permission denied" )

		if restart:
			u.startProc( m, p.name )

		m.killProc( p, signal )

		raise redirect( "procs", user=u.name )
	# killproc


	@identity.require( Permission( 'modify' ) )
	@expose()
	@validate( validators = dict( pid = validators.Int() ) )
	def retireApp( self, machine, pid ):
		c = cluster.cache.get()
		m = c.getMachine( machine )
		p = m.getProc( pid )

		if not p:
			raise ServerStateException(
				"No process with machine '%s' and PID '%d'" % ( machine, pid ) )

		u = p.user()

		if util.getServerUsername() != u.name:
			raise AuthorisationException( "Permission denied" )

		p.retireApp()

		raise redirect( 'procs', user=u.name )
	# retireApp


	@identity.require( Permission( 'modify' ) )
	@expose()
	@util.unicodeToStr
	def doStart( self, mode, group=None, machine=None, layout=None,
				 restrict=False ):

		c = cluster.cache.get()
		kw = {}

		# Saved layout mode
		if mode == "layout":
			rec = self.getLayout( layout )
			if not rec:
				return self.error( "Couldn't find saved layout '%s' "
								   "in the database" % layout )
			user = c.getUser( util.getServerUsername(), fetchVersion = True )
			task = async_task.AsyncTask( 0, user.startFromXML,
										 StringIO( rec.xmldata ) )

		# Single and group modes
		else:
			if mode == "single":
				machines = [c.getMachine( machine )]
				# Use that machine to resolve the user.
				user = c.getUser( util.getServerUsername(),
					machine = machines[0], fetchVersion = True )
				kw[ "useSimpleLayout" ] = True
			else:
				machines = None
				user = c.getUser( util.getServerUsername(),
								fetchVersion = True )

			if mode == "group":

				# If the selected group is all machines, force the group
				# to be None. This will replicate the behavior of
				# 'cluster_control.py start all'
				if group == "(use all machines)":
					group = None

				kw[ "group" ] = group
				if restrict:
					kw[ "tags" ] = True

			task = async_task.AsyncTask( 0, user.start, machines, **kw )


		# Setup prefs kw
		startPrefsKW = {}
		startPrefsKW[ "user" ] = util.getSessionUser()
		startPrefsKW[ "last_mode" ] = mode

		if mode == "single":
			startPrefsKW[ "last_machine" ] = machine
			startPrefsKW[ "useTags" ] = bool( restrict )

		elif mode == "group":
			startPrefsKW[ "last_group" ] = group
			startPrefsKW[ "useTags" ] = bool( restrict )

		elif mode == "layout":
			startPrefsKW[ "last_layout" ] = layout
			startPrefsKW[ "useTags" ] = False

		# Determine whether inserting or updating
		count = 0

		for rec in model.ccStartPrefs.select(
			model.ccStartPrefs.q.userID == util.getSessionUID() ):

			count += 1
			if count == 1:
				# Use the SQLObject set (update) functionality instead
				rec.set( **startPrefsKW )
			else:
				# Delete duplicates (should not be any)
				rec.destroySelf()

		if count == 0:
			# none found for update, create the record.
			
			# First ensure that all mode-dependant fields have values before
			# adding. This will prevent an SQLObject error which expects these
			# fields.
			if not "last_machine" in startPrefsKW:
				startPrefsKW[ "last_machine" ] = ""
			if not "last_group" in startPrefsKW:
				startPrefsKW[ "last_group" ] = ""
			if not "last_layout" in startPrefsKW:
				startPrefsKW[ "last_layout" ] = ""
			if not "useTags" in startPrefsKW:
				startPrefsKW[ "useTags" ] = False

			model.ccStartPrefs( **startPrefsKW )


		# Block until we get the layout out of the async task
		try:
			layout = task.waitForState( "layout" )[1][:]
		except task.TerminateException:
			return self.error( "Couldn't get layout" )

		# Tag each process as "running"
		for i in xrange( len( layout ) ):
			layout[i] = layout[i] + ("running",)

		return self.toggle( "start", task.id, layout, user )
	# doStart


	@identity.require( Permission( 'modify' ) )
	@expose()
	def restart( self ):

		c = cluster.cache.get()
		user = c.getUser( util.getServerUsername(), fetchVersion = True )
		layout = user.getLayout()
		self.appendToLayout( layout, "registered" )
		task = async_task.AsyncTask( 0, user.restart )
		return self.toggle( "restart", task.id, layout, user )
	# restart


	@identity.require( Permission( 'modify' ) )
	@expose()
	def stop( self ):

		user = util.getServerUsername()

		c = cluster.cache.get()
		user = c.getUser( user, fetchVersion = True )
		layout = user.getLayout()
		self.appendToLayout( layout, "registered" )
		task = async_task.AsyncTask( 0, user.smartStop )
		return self.toggle( "stop", task.id, layout, user )
	# stop


	@identity.require( Permission( 'modify' ) )
	@expose()
	def kill( self ):
		"""
		Kill the server.  Data loss may occur if BaseApps are in the
		process of writing entities to the database.
		"""
		user = util.getServerUsername()

		c = cluster.cache.get()
		user = c.getUser( user, fetchVersion = True )
		layout = user.getLayout()
		self.appendToLayout( layout, "registered" )
		task = async_task.AsyncTask( 0, user.smartStop, forceKill=True )
		return self.toggle( "stop", task.id, layout, user )
	# kill


	@identity.require( Permission( 'modify' ) )
	@expose( template="cluster_control.templates.toggle" )
	def toggle( self, action, id, layout, user="TODO_fixClientLinksThenRemoveMe" ):

		user = util.getServerUsername()

		# Figure out pnames set
		pnames = set()
		for _, pname, _, _ in layout:
			pnames.add( pname )
		pnames = list( pnames )
		pnames.sort( process_module.Process.cmpByName )

		return dict( action = action, layout = layout,
					 pnames = pnames, user = user, id = id )
	# toggle


	@identity.require( identity.not_anonymous() )
	@ajax.expose
	def verifyEnv( self, type, value ):

		user = util.getServerUsername()
		c = cluster.cache.get()
		ms = []

		if type == "machine":
			mname = c.getMachine( value )
			if not mname:
				raise ajax.Error( "Unknown machine: '%s'" % value )
			ms.append( mname )

		elif type == "group":
			groups = c.getGroups()
			if value == "(use all machines)":
				ms = c.getMachines()
			elif groups.has_key( value ):
				ms = groups[ value ]
			else:
				raise ajax.Error( "Unknown group: %s" % value )

		elif type == "layout":
			layout = self.getLayout( value )
			if not layout:
				raise ajax.Error( "Unknown layout: '%s'" % value )
			mnames = [m for ( m,p ) in user_module.User.parseXMLLayout( layout.xmldata )]

			ms = []; missing = False
			for mname in mnames:
				ms.append( c.getMachine( mname ) )
				if not ms[-1]:
					log.error( "Layout refers to unknown machine '%s'", mname )
					missing = True

			if missing:
				raise ajax.Error( "Layout refers to unknown machines" )
		else:
			raise ajax.Error( "Invalid or missing type argument" )

		user = c.getUser( user, random.choice( ms ), refreshEnv = True,
					fetchVersion = True )

		if user.verifyEnvSync( ms ):
			return dict( mfroot = user.mfroot, bwrespath = user.bwrespath )

		else:
			raise ajax.Error(
				"Inconsistent environment settings across target machines" )
	# verifyEnv


	@identity.require( Permission( 'view' ) )
	@expose( template="cluster_control.templates.coredumps" )
	def coredumps( self ):

		user = util.getServerUsername()

		c = cluster.cache.get( user = user )
		user = c.getUser( user, checkCoreDumps = True )
		coredumps = sorted( user.coredumps, key = lambda x: x[2] )
		return dict( user = user, coredumps = coredumps )
	# coredumps


	# --------------------------------------------------------------------------
	# Section: Saved XML layouts
	# --------------------------------------------------------------------------

	@util.unicodeToStr
	def getLayout( self, name ):
		recs = list( model.ccSavedLayouts.select( sqlobject.AND(
			model.ccSavedLayouts.q.userID == util.getSessionUID(),
			model.ccSavedLayouts.q.name == name ) ) )
		if len( recs ) == 1:
			return recs[0]
		elif len( recs ) == 0:
			return None
		else:
			log.critical( "Multiple saved layouts called '%s' exist for %s",
						  name, util.getSessionUsername() )
	# getLayout


	@identity.require( Permission( 'view' ) )
	@ajax.expose
	def saveLayout( self, name ):

		user = util.getServerUsername()

		c = cluster.cache.get()
		user = c.getUser( user )
		stream = StringIO()
		user.saveToXML( stream )

		# Delete any existing query with the same name
		old = self.getLayout( name )
		if old:
			old.destroySelf()

		model.ccSavedLayouts( user = util.getSessionUser(),
							  name = name,
							  serveruser = user.name,
							  xmldata = stream.getvalue() )

		return "Server layout saved successfully"
	# saveLayout


	@identity.require( identity.not_anonymous() )
	@expose()
	def deleteLayout( self, name ):
		rec = self.getLayout( name )
		if not rec:
			return self.error( "Can't delete non-existent layout '%s'" % name )
		else:
			rec.destroySelf()
			raise redirect( "layouts" )
	# deleteLayout


	@identity.require( identity.not_anonymous() )
	@expose( template="web_console.cluster_control.templates.layouts" )
	def layouts( self ):
		recs = model.ccSavedLayouts.select(
			model.ccSavedLayouts.q.userID == util.getSessionUID() )

		# Convert each XML layout into a mapping of process counts
		layouts = []
		pnames = set()
		for rec in recs:
			counts = {}
			layout = user_module.User.parseXMLLayout( rec.xmldata )
			for mname, pname in layout:
				pnames.add( pname )
				if counts.has_key( pname ):
					counts[ pname ] += 1
				else:
					counts[ pname ] = 1
			layouts.append( counts )

		# Not all layouts have the same types of server processes.
		# If a particular process type ( e.g. bots ) is missing, set
		# count for that process type to 0.
		for counts in layouts:
			for pname in pnames.difference( counts.keys() ):
				counts[ pname ] = 0

		# Sort pnames by pre-arranged ordering here
		pnames = list( pnames )
		pnames.sort( process_module.Process.cmpByName )

		return dict( recs = recs, layouts = layouts, pnames = pnames )
	# layouts


	@identity.require( identity.not_anonymous() )
	@expose( template="web_console.common.templates.error" )
	def error( self, message ):
		return util.getErrorTemplateArguments( message )
	# error

# end class ClusterControl

# controllers.py
