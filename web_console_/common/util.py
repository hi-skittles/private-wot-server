import re
import os
import sys
import logging
import zipfile
import stat
import time
import cgi

import cherrypy
import turbogears
from turbojson import jsonify

import bwsetup; bwsetup.addPath( "../.." );
from pycommon import user as user_module
from pycommon import cluster as cluster_module
from pycommon.exceptions import IllegalArgumentException

import format_docs

from web_console.common.authorisation_filter import AuthorisationFilter

log = logging.getLogger( __name__ )


def alterParams( **kw ):
	path = cherrypy.request.path
	params = dict( cherrypy.request.params )

	params.update( kw )
	return turbogears.url( path, **params )


def getSessionUsername():
	idobj = cherrypy.request.identity
	if idobj.anonymous:
		return None
	else:
		return idobj.user.user_name

def getSessionUser():
	idobj = cherrypy.request.identity
	if idobj.anonymous:
		return None
	else:
		return idobj.user

def getSessionUID():
	idobj = cherrypy.request.identity
	if idobj.anonymous:
		return None
	else:
		return idobj.user.id


def getServerUsername():

	idobj = cherrypy.request.identity

	if idobj.anonymous:
		return None

	actingServerUser = getattr( idobj, AuthorisationFilter.ACTING_USER_KEY, None )

	if actingServerUser:
		return actingServerUser
	else:
		return idobj.user.serveruser
# getServerUsername


def getUser( cluster, username = None, fetchVersion = False  ):
	"""
	Fetch the User object for the given username, or for the current
	server user if username is None.
	"""

	if not cluster.getMachines():
		raise turbogears.redirect(
			"/error", msg = "No bwmachined daemons are running")

	try:
		if not username:
			username = getServerUsername()
		return cluster.getUser( username, fetchVersion = fetchVersion )
	except user_module.UserError:
		raise turbogears.redirect(
			"/error", msg = "Couldn't resolve user %s" % username )
# getUser


def getProcsOfUser( cluster = None, username = None ):
	"""
	Fetch the processes for the given user in given cluster, or for the current
	server user if username is None
	"""

	if not cluster:
		cluster = cluster_module.cache.get()

	user = getUser( cluster, username );

	return user.getProcs()
# getProcsOfUser


def getProcsOfUserSortedByLabel( cluster = None, username = None ):
	"""
	Fetch the processes for the given user in given cluster, or for the current
	server user if username is None
	"""

	procs = getProcsOfUser( cluster, username )
	procs.sort( lambda x, y: cmp( x.label(), y.label() ) )

	return procs
# getProcsOfUserSortedByLabel


def isFileReadableByOthers( filePath ):
	try:
		st = os.stat( filePath )
	except Exception, ex:
		log.error( "Failed to stat file:", filePath )
		return False

	if st.st_mode & stat.S_IROTH:
		return True
	else:
		return False


def getErrorTemplateArguments( message, error='ERROR', traceback=None,
								timestamp=None ):
	"""
	Builds the common arguments that need to be passed the error template. These
	are also returned if an error page is returned via the API.

	@param message: The main message to display on the template
	@param error: The heading to display in bold on the page. Default is "ERROR"
	@param traceback: The stack trace to display. Default is None.
	@param timestamp: The time string to display. Defaults is now.
	@return: A dictionary containing the final computed values.
	"""
	if not timestamp:
		timestamp = time.ctime()
	return dict(
		message = message,
		error = error,
		traceback = traceback,
		timestamp = timestamp
	)

# ------------------------------------

# ------------------------------------------------------------------------------
# Section: Decorators
# ------------------------------------------------------------------------------

def unicodeToStr( f ):
	"""
	Converts unicode arguments to UTF-8 strings which are used all through
	WebConsole apart from MessageLogger queries. This is useful because
	SQLObject doesn't deal nicely with unicode and doing string == doesn't
	work with unicode.
	"""

	def execute( *args, **kw ):

		for i in xrange( len( args ) ):
			if isinstance( args[ i ], unicode ):
				if isinstance( args, tuple ):
					args = list( args )
				args[ i ] = args[ i ].encode( "utf-8" )

		for k, v in kw.items():
			if isinstance( v, unicode ):
				kw[ k ] = v.encode( "utf-8" )

		return f( *args, **kw )

	return execute


def unzip( zipPath, dirName ):
	log.debug( "opening zip file %s" % zipPath )
	zf = zipfile.ZipFile( zipPath )
	extractFile = None

	try:
		infoList = zf.infolist()
		for info in infoList:
			log.debug( "unzipping %s..." % info.filename )

			# is it a dir?
			if info.filename.endswith( '/' ):
				# user and group read, write and executable
				os.umask( 0007 )
				os.mkdir( info.filename )
			else:
				contents = zf.read( info.filename )

				extractFile = open( dirName + os.sep + info.filename, "w" )
				extractFile.write( contents )
				extractFile.close()
				extractFile = None
	finally:
		if extractFile:
			extractFile.close()
		zf.close()


def addContentsToHTML():
	"""
	This method generates a table of contents for each file named *.notoc.html
	in the web_console tree.
	"""

	wcroot = os.path.abspath( bwsetup.appdir + "/.." )

	for path in os.popen( "find %s -name '*.notoc.html'" % wcroot ):

		path = path.strip()
		dir, fname = os.path.split( path )
		rawpath = "%s/%s" % (dir, fname.replace( ".notoc.html", ".html" ))

		if not os.path.exists( rawpath ) or \
		   os.stat( path ).st_mtime > os.stat( rawpath ).st_mtime:
			format_docs.process( path, open( rawpath, "w" ) )
			log.info( "Generated TOC for %s",
						path.replace( wcroot + "/", "" ) )


def forbidEmptyArguments( fn ):
	"""
	Decorator to forbid any of the wrapped function's arguments from being empty
	"""
	def raiseIfEmpty( name, value ):
		# Value is a FieldStorage object when uploading a file. A bug in Python 
		# versions < 2.7 makes bool(FieldStorage) resolve to False even if the 
		# object is not empty. Set value to file attribute of object.
		if isinstance( value, cgi.FieldStorage ) \
				and sys.version_info < ( 2, 7 ):
			value = value.file

		if not value:
			# Put quotes around variable with known names
			if ' ' in name:
				displayName = name
			else:
				displayName = "'%s'" % name
			raise IllegalArgumentException( argName=name, argValue=value,
					message="No value provided for %s" % displayName )

	def wrapped( *anonymousArgs, **namedArgs ):
		for i, value in enumerate( anonymousArgs ):
			raiseIfEmpty( 'argument %d' % i, value )
		for name, value in namedArgs.iteritems():
			raiseIfEmpty( name, value )
		return fn( *anonymousArgs, **namedArgs )

	return wrapped


class ActionMenuOptions( object ):
	"""
	This is a helper class that must be passed to actionMenu() in
	web_console.common.templates.common.kid.  It has support for option groups
	and can assign XML ids to them.  Actual options can either be redirects or
	javascript calls.
	"""

	class Group( object ):
		def __init__( self, name, id ):
			self.name = name
			self.id = id
			self.options = []
		# __init__

		def __json__( self ):
			return self.__dict__
		# __json__
	# end class Group


	def __init__( self ):
		self.groups = {}
		self.groupOrder = []
	# __init__


	def __json__( self ):
		return self.groupOrder
	# __json__


	def addGroup( self, name, id = "" ):
		group = self.Group( name, id )
		self.groups[ name ] = group
		self.groupOrder.append( group )
		return group


	def addRedirect( self, label, href, params = {}, help = "",
					 group = "Action..." ):
		"""
		Add a menu option that will do a redirect when clicked.  The URL can be
		provided entirely inline in the 'href' argument, or the base URL can be
		passed as 'href' and 'params' will be appended as querystring params.
		"""

		try:
			group = self.groups[ group ]
		except KeyError:
			group = self.addGroup( group )

		if params:
			href = turbogears.url( href, **params )

		group.options.append( (label, "window.location = '%s'" % href, help) )


	def addScript( self, label, script, args = None, help = "",
				   group = "Action..." ):
		"""
		Add a menu option that is a JavaScript call.  The call can be provided
		entirely inline in the 'script' argument (with 'args' left as None), or
		if 'args' is passed, the call will be interpreted as 'script( *args )'.
		"""

		try:
			group = self.groups[ group ]
		except KeyError:
			group = self.addGroup( group )

		# If javascript args have been provided, transform the script into a
		# function call
		if args is not None:
			script = ("%s(" % script) + \
					 ",".join( map( jsonify.encode, args ) ) + ")"
			script = re.sub( '"', "'", script )

		group.options.append( (label, script, help) )

# util.py
