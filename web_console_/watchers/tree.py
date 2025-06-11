import os
import logging
import turbogears

from turbogears import expose
from turbogears import identity
from turbogears import redirect
from turbogears import validate
from turbogears import validators

from web_console.common import util
from web_console.common.authorisation import Permission
from pycommon import cluster
from pycommon import watcher_data_type as WDT
from pycommon import process as process_module

import collections as collections_module

log = logging.getLogger( __name__ )


class Tree( turbogears.controllers.Controller ):

	@identity.require( Permission( 'view' ) )
	@expose( template="watchers.templates.tree_processes" )
	@util.unicodeToStr
	def index( self ):
		c = cluster.cache.get()

		user = util.getUser( c, None )
		# TODO: should this be user.getServerProcs?
		processes = user.getProcs()
		processes.sort( lambda x, y: cmp( x.label(), y.label() ) )

		return dict( user = user, processes = processes )


	@identity.require( Permission( 'modify' ) )
	@expose( template="watchers.templates.tree_edit" )
	@validate( validators={"propagate":validators.Bool(), "pid":validators.Int()} )
	@util.unicodeToStr
	def edit( self, machine, path, pid, propagate=False, newval=None, dataType=None ):
		c = cluster.cache.get()
		m = c.getMachine( machine )
		p = m.getProc( int( pid ) )
		if not p:
			raise redirect( "/error",
					message = "Process %s no longer exists" % pid )

		try:
			wd = p.getWatcherData( path )
		except TypeError, e:
			# It is possible that a type error will be thrown if the process
			# does not support querying the watcher tree.
			raise redirect( "/error", message = str( e ) )

		processes = []
		if propagate:
			user = util.getUser( c, None )
			processes = user.getProcs( p.name )
			processes.sort( lambda x, y: cmp( x.label(), y.label() ) )

		if newval:
			log.info( "Setting a new value" )

			if dataType != None:
				wdtClass = WDT.WDTRegistry.getClass( int(dataType) )
				newval = wdtClass( newval )

			error = None

			if propagate:
				error = ""

				for proc in processes:
					try:
						procwd = proc.getWatcherData( path )
						if not procwd.set( newval ):
							if error != "":
								error += ", "
							error += "\"Failed to set value on " + \
								proc.label() + "\""
					except TypeError, e:
						if error != "":
							error += ", "
						error += "\"Failed to find watcher on " + \
								proc.label() + "\""
						pass

				if error == "":
					error = None
			else:
				if not wd.set( newval ):
					error = "\"Failed to find watcher on " + \
						p.label() + "\""


			wd = p.getWatcherData( os.path.dirname( wd.path ) )
			raise redirect( "/watchers/tree/show", machine = machine, pid = pid,
					path = os.path.dirname( path ), error = error )

		values = []

		if propagate:
			processes.sort( lambda x, y: cmp( x.label(), y.label() ) )

			for proc in processes:
				try:
					procwd = proc.getWatcherData( path )
					values.append( ( proc.label(), procwd.value ) )
				except TypeError, e:
					pass


		return dict( process = p, machine = m, watcherData = wd,
				propagate = propagate, values = values )


	@identity.require( Permission( 'view' ) )
	@expose( template="watchers.templates.tree" )
	@util.unicodeToStr
	def show( self, machine, pid, path="", error = False ):
		c = cluster.cache.get()
		m = c.getMachine( machine )
		p = m.getProc( int( pid ) )
		if not p:
			raise redirect( "/error",
					message = "Process %s no longer exists" % pid )

		try:
			wd = p.getWatcherData( path )
		except TypeError, e:
			# It is possible that a type error will be thrown if the process
			# does not support querying the watcher tree.
			raise redirect( "/error", message = str( e ) )

		children = wd.getChildren()
		subdirs = []
		watchersList = []
		if children:
			subdirs = [c for c in children if c.isDir()]
			watchersList = [c for c in children if not c.isDir()]

		collections = list( collections_module.getCollections() )

		authUser = identity.current.user
		watchers = []
		for w in watchersList:
			# Unfortunately this menu is created here because
			# the list of watchers is generated above
			# (this should be moved into controllers.py)
			menu = util.ActionMenuOptions()
			menu.addGroup( "Action..." )
			if w.isCallable():
					menu.addRedirect( "Commands Page",
							turbogears.url("/commands"),
							help="Visit the commands page" )
			else:
				if not w.isReadOnly() and authUser.hasPermissions( 'modify' ):
					menu.addRedirect( "Edit this process",
							turbogears.url("/watchers/tree/edit",
								machine = machine, pid = pid, path = w.path ),
							help="Edit this watcher value" )

					if p.name not in process_module.Process.types.singletons():
						menu.addRedirect( "Edit all %s processes" % p.name,
							turbogears.url("/watchers/tree/edit",
								machine = machine, pid = pid, path = w.path,
								propagate = True ),
							help="Edit this watcher value on all processes" )

				if p.name in process_module.Process.types.startable():
					menu.addGroup( "Add to Collection..." )
					for collection in collections_module.getCollections():
						menu.addScript( "%s" % collection.pageName,
							args = ( collection.pageName, p.name, w.path ),
							group = "Add to Collection...",
							script = "addToCollection" )

					menu.addScript( "Create filtered view",
							args = (p.name, w.path),
							script = "createFilteredView" )

			watchers.append( (w, menu) )

		return dict( process = p, machine = m, error = error,
				watcherData = wd, subDirs = subdirs, watchers = watchers )

# tree.py
