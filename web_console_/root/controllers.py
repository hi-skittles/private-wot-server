# Standard Python includes
import traceback
import sys
import os
import time
import logging
import inspect
import mimetypes
import simplejson as json
from StringIO import StringIO

# Turbogears stuff
import cherrypy
import turbogears
from turbogears import controllers, expose, redirect, identity, config, visit
from turbogears import validate, validators

# Other BigWorld python modules
import bwsetup;
bwsetup.addPath( "../.." )

from web_console.common import model
from web_console.common import util
from web_console.common import ajax
from web_console.common.authorisation import Permission
from web_console.common.authorisation_filter import AuthorisationFilter
from web_console.root import version_info
from web_console.root.user_feedback import UserFeedback
from pycommon import async_task
from pycommon import cluster
from pycommon.exceptions import AuthenticationException, AuthorisationException

log = logging.getLogger( __name__ )


class Root( controllers.RootController ):

	# maps exception class name to HTTP status code
	# see: http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
	HTTP_RESPONSE_CODE = {
		"Exception": 500,                     # "Internal Server Error"
		"NotImplementedError": 501,           # "Not Implemented"
		"AuthenticationException": 403,       # "Forbidden"
		"AuthorisationException": 403,        # "Forbidden"
		"ServerStateException": 455,          # "Method Not Valid in This State"
	}

	VERSION_INFO = None

	# list of CherryPy filters that will apply to this and all
	# descendant controllers; see CherryPy docs
	_cp_filters = []


	def __init__( self, *args, **kw ):
		controllers.RootController.__init__( self, *args, **kw )

		# This doesn't actually prevent people from accessing these pages, it
		# just prevents links to these pages being shown in the nav menu
		isAdmin = lambda: "admin" in cherrypy.request.identity.groups
		
		import web_console.database_admin.controllers
		self.dba = web_console.database_admin.controllers.DBAIndex(
			parent = self,
			name = "Database",
			path = "dba",
			icon = "/static/images/admin.png",
			auth = Permission( 'view' ) )

		import web_console.cluster_control.controllers
		self.cc = web_console.cluster_control.controllers.ClusterControl(
			parent = self,
			name = "Cluster",
			path = "cc",
			icon = "/static/images/cluster_control.png",
			auth = Permission( 'view' ),
			help = "cluster_control/static/html/help.html" )

		import web_console.watchers.controllers
		self.watchers = web_console.watchers.controllers.Watchers(
			parent = self,
			name = "Watchers",
			path = "watchers",
			icon = "/static/images/watchers.png",
			auth = Permission( 'view' ),
			help = "watchers/static/html/help.html" )

		import web_console.log_viewer.controllers
		self.log = web_console.log_viewer.controllers.LogViewer(
			parent = self,
			name = "Logs",
			path = "log",
			icon = "/static/images/log_viewer.png",
			auth = Permission( 'view' ),
			help = "log_viewer/static/html/help.html" )

		if config.get( "web_console.spaces.on", True ):
			import web_console.space_viewer.controllers
			self.sv = web_console.space_viewer.controllers.SpaceViewerController(
				parent = self,
				name = "Spaces",
				path = "sv",
				icon = "/static/images/sv.png",
				auth = Permission( 'view' ),
				help = "space_viewer/static/html/help.html" )

		if config.get( "web_console.old_graphs.on", True ):
			import web_console.stat_grapher.controllers
			self.statg = web_console.stat_grapher.controllers.StatGrapher(
				parent = self,
				name = "Graphs",
				path = "statg",
				icon = "/static/images/stat_grapher.png",
				auth = Permission( 'view' ),
				help = "stat_grapher/static/html/help.html" )

		if config.get( "web_console.graphs.on", False ):
			from web_console.graphs.controllers import GraphsController
			self.graphs = GraphsController(
				parent = self,
				name = "Graphs",
				path = "graphs",
				icon = "/static/images/stat_grapher.png",
				auth = Permission( 'view' ),
				help = "graphs/static/html/help.html" )

		import web_console.console.controllers
		self.console = web_console.console.controllers.Console(
			parent = self,
			name = "Consoles",
			path = "console",
			icon = "/static/images/console.png",
			auth = Permission( 'view', 'modify' ),
			help = "console/static/html/help.html" )

		import web_console.commands.controllers
		self.commands = web_console.commands.controllers.Commands(
			parent = self,
			name = "Commands",
			path = "commands",
			icon = "/static/images/commands.png",
			auth = Permission( 'view', 'modify' ),
			help = "commands/static/html/help.html" )

		import web_console.admin.controllers
		self.admin = web_console.admin.controllers.Admin(
			parent = self,
			name = "Admin",
			path = "admin",
			icon = "/static/images/admin.png",
			auth = isAdmin,
			help = "admin/static/html/help.html" )

		if config.get( 'web_console.profiler.on', False ):
			from web_console.profiler.controllers import ProfilerController
			self.profiler= ProfilerController(
				parent = self,
				name = "Profiler",
				path = "profiler",
				icon = "/static/images/profiler.png",
				auth = Permission( 'view' ),
				help = "profiler/static/html/help.html" )

		if turbogears.config.get( 'web_console.http_api.on', False ):
			from web_console.api.controllers import HttpApi
			self.api = HttpApi(
				parent = self,
				name = "API",
				path = "api",
				icon = "/static/images/admin.png",
				auth = Permission( 'view' ) )


		self.userFeedback = UserFeedback()

	# __init__


	@classmethod
	def onStartServer( self ):

		model.init()

		if turbogears.config.get( 'web_console.authorisation.on', False ):
			Root._cp_filters.append( AuthorisationFilter() )

		if config.get( 'web_console.analytics.on', False ):
				from web_console.common.analytics_filter import AnalyticsFilter
				Root._cp_filters.append( AnalyticsFilter() )

		# init upload director
		uploadDir = config.get( 'web_console.upload_directory' )
		if uploadDir and not os.path.exists( uploadDir ):
			os.makedirs( uploadDir )

		Root.VERSION_INFO = version_info.load()

	# onStartServer


	### for testing, though could be good to expose in JSON api ###
	@expose( "json" )
	def permissions( self ):
		return Permission.getPermissionsByMethod()
	# perms


	def handleException( self, status = 500, message = None ):
		""" CherryPy HTTP error handler callback.

			Response to client depends on request Accept header: if
			Accept header contains C{"application/json"}, a JSON response is sent to
			the client, together with a HTTP response code derived from the
			L{Exception}'s python class (see L{HTTP_RESPONSE_CODE}). Otherwise, a
			HTML page with the error is returned with HTTP status 200 OK.

			For further info on error callbacks, see:
			http://www.cherrypy.org/chrome/common/2.2/docs/book/chunk/ch03s03.html#specialfunctions
			"""

		# thread-safe, sys.exc_info is per-thread
		exception = sys.exc_info()[1]

		# this method should only be called because an Exception was thrown while
		# processing a HTTP request
		assert exception, "Expected an exception"

		# cherrypy adds an extra argument to the 'args' tuple property of any
		# uncaught exception that is thrown during a HTTP request, so here we
		# pop it off and assign to a property, else it screws up rendering
		# exceptions as strings
		if exception.args[-1].__class__.__name__ in ('function', 'instancemethod'):
			exception.origin = exception.args[-1]
			exception.args = exception.args[:-1]

		# if you ask for json, you must get json
		if 'application/json' in cherrypy.request.headers['Accept']:
			# render a JSON response
			self.createErrorJson( exception )
		else:
			# Render a HTML page
			self.createErrorPage( exception, status, message )
	# handleError


	# Attach error handler to CherryPy
	_cp_on_http_error = handleException


	@expose( "json" )
	def getFeedbackData( self ):
		return self.userFeedback.getFeedbackData( self.VERSION_INFO )


	@expose( "json" )
	def sendFeedbackEmail( self, subject, returnAddress, comments,
			exceptionData ):
		return dict( success = self.userFeedback.sendEmail(
			subject, returnAddress, comments, exceptionData,
				self.VERSION_INFO ) )


	def createErrorJson( self, exception ):
		""" Sets HTTP headers and body of the current HTTP request response with an
			appropriate JSON response for the passed Exception. """
		status, message = self.getHttpResponse( exception )

		if (status >= 500):
			# print exception's stack trace if status >= 500
			trace = traceback.format_exc()
			log.error( "Uncaught Exception:\n%s: %s for user %s\n%s",
				exception.__class__.__name__, message, util.getServerUsername(),
				trace )
		else:
			log.warning( "%s: %s for user %s",
				exception.__class__.__name__, message, util.getServerUsername() )

		log.info( "rendering exception as JSON due to Accept header" )
		body = json.dumps( {
			"status": status,
			"message": message,
			"exception": exception.__class__.__name__
		} )

		cherrypy.response.status = status
		cherrypy.response.headers['Content-Length'] = len( body )
		cherrypy.response.body = body
	# createErrorJson


	def createErrorPage( self, exception, status = 500, message = None ):
		""" Renders a HTML error page for the passed Exception. """

		template = "web_console.common.templates.error"

		# don't create HTML pages for image requests
		i = cherrypy.request.path.rfind( '.' )
		if i != -1:
			extension = cherrypy.request.path[i:].lower()
			contentType = mimetypes.types_map.get( extension, '' )
			if contentType.startswith( 'image' ):
				cherrypy.response.status = status
				#cherrypy.response.headers['Content-Type'] = contentType
				cherrypy.response.body = \
					"The path '%s' could not be found" % (cherrypy.request.path,)
				return

		if isinstance( exception, AuthorisationException ):
			# message = str( exception )
			status, message = self.getHttpResponse( exception )
			output = util.getErrorTemplateArguments( message )

			log.warning( "%s: %s for user '%s'",
				exception.__class__.__name__, message, util.getSessionUsername() )

		elif isinstance( exception, AuthenticationException ):
			# message = message or str( exception )
			status, message = self.getHttpResponse( exception )
			log.warning( "%s: %s for user '%s'",
				exception.__class__.__name__, message, util.getSessionUsername() )

			if identity.not_anonymous():
				message = "You don't have sufficient permissions for this resource"
			else:
				message = 'You must be logged in to access this page'

			output = util.getErrorTemplateArguments(
				message = message,
				error = 'Access Denied',
			)

		elif isinstance( exception, cherrypy.HTTPError ):

			status = exception.status or 500
			message = exception.message or ''

			error = {
				400: u'400 - Bad Request',
				401: u'401 - Unauthorized',
				403: u'403 - Forbidden',
				404: u'404 - Not Found',
				500: u'500 - Internal Server Error',
				501: u'501 - Not Implemented',
				502: u'502 - Bad Gateway',
			}.get( exception.status, message or u'General Error' )

			output = util.getErrorTemplateArguments(
				message = message,
				error = error,
			)

			log.error( "HTTP error %s: %s( %s )",
				status, exception.__class__.__name__, message )

		else:
			if identity.not_anonymous():
				trace = traceback.format_exc()
			else:
				trace = None
			status = 500

			output = util.getErrorTemplateArguments(
				message = str( exception ),
				error = 'Exception Raised',
				traceback = trace,
			)

			log.error( "Uncaught Exception:\n%s( %s ):\n%s",
				exception.__class__.__name__, output[ "message" ], output[ "traceback" ] )

		log.info( "rendering HTML page for uncaught %s", exception.__class__.__name__ )
		format = 'html'
		content_type = 'text/html'
		mapping = None

		# render template
		body = controllers._process_output(
			output, template, format, content_type, mapping )

		cherrypy.response.headers['Content-Length'] = len( body )
		cherrypy.response.status = status
		cherrypy.response.body = body

	# createErrorPage


	def getHttpResponse( self, exception ):
		""" Return the best-matched HTTP response code and message for the given
			exception. If the passed exception defines a __http_response__ method,
			its return value will be returned, else the return value will be based
			on the class name of the exception. """

		if isinstance( exception, cherrypy.HTTPError ):
			return (exception.status, exception.message)

		if hasattr( exception, "__http_response__" ):
			return exception.__http_response__()

		if hasattr( exception.__class__, "mro" ):
			# new-style class; python 2.2+
			superclasses = exception.__class__.mro()
		else:
			# old-style class
			superclasses = (exception.__class__,) + exception.__class__.__bases__

		for classObj in superclasses:
			if classObj.__name__ in self.HTTP_RESPONSE_CODE:
				return (
					self.HTTP_RESPONSE_CODE[ classObj.__name__ ],
					str( exception[0] )
				)

		return (500, str( exception ))
	# getHttpResponseCode


	@identity.require( identity.not_anonymous() )
	@expose( template = "web_console.common.templates.error" )
	def exception( self, enum ):
		e = "Exception number '%s' is invalid." % enum
		t = ""
		etime = None
		try:
			(e, t, etime) = ajax.exceptions[ int( enum ) ]
		except (ValueError, KeyError):
			# Invalid int or missing key, don't do anything more
			pass
		return util.getErrorTemplateArguments(
			message = e,
			error = "Exception Raised",
			traceback = t,
			timestamp = time.ctime( etime )
		)


	@expose( "web_console.common.templates.login" )
	def index( self ):
		if identity.current.anonymous:
			return {}
		elif "admin" in cherrypy.request.identity.groups:
			return redirect( "admin" )
		else:
			# Go straight to cc/procs, saving one redirect via cc/
			return redirect( "cc/procs" )


	@expose( "json" )
	def auth( self ):
		if (not identity.current.anonymous and identity.was_login_attempted() and
			not identity.get_identity_errors()):
			sessionParamName = turbogears.config.get( 'visit.form.name' )
			sessionId = identity.current.visit_key
			return { sessionParamName: sessionId }
		else:
			raise AuthenticationException( "Login incorrect" )
	# auth


	@expose( "json" )
	def version( self ):
		return Root.VERSION_INFO

	def checkLoginCommon( self ):
		"""
		Check whether the current login is correct.

		@return (boolean whether successful, error message)
		"""
		new_visit = visit.current()
		if new_visit:
			new_visit = new_visit.is_new

		if (not new_visit and not identity.current.anonymous
				and identity.was_login_attempted()
				and not identity.get_identity_errors()):
			# Successful login
			return True, None
		elif identity.was_login_attempted():
			# Deal with the failure possibilities
			if new_visit:
				errorMsg = u"Cannot log in because your browser " + \
						"does not support session cookies"
			else:
				# Username & password failed
				errorMsg = u"Login incorrect"
		elif identity.get_identity_errors():
			# Not sure what triggers this section
			errorMsg = u"Login incorrect"
			# errorMsg = u"You must provide your credentials before " + \
			#		 "accessing this resource."
		elif identity.not_anonymous():
			# Triggered if you just go straight to /login while logged in
			return True, None
		else:
			# Triggered if you just go straight to /login without logging in
			errorMsg = u"Please log in"
		return False, errorMsg

	def checkLoginJson( self ):
		"""
		AJAX login check
		@return: JSON on success, raise a 403 on failure
		"""
		success, errorMsg = self.checkLoginCommon()

		if success:
			return dict(
				loginSuccess = True
			)
		else:
			raise AuthenticationException( errorMsg )

	def checkLoginHtml( self, **kw ):
		"""
		HTML login check
		@return: HTTP redirect on success, fields to render template on failure
		"""
		success, errorMsg = self.checkLoginCommon()

		if success:
			redirect( '/', kw )
		else:
			return dict(
				loginSuccess = False,
				loginErrors = errorMsg,
			)

	@expose( "web_console.common.templates.login", allow_json=True )
	def login( self, *args, **kw ):
		# Different response types depending on whether it's called from
		# AJAX or HTML
		if 'application/json' in cherrypy.request.headers['Accept']:
			return self.checkLoginJson()
		else:
			return self.checkLoginHtml( **kw )

	@expose()
	def logout( self ):
		cherrypy.request.identity.logout()
		raise redirect( "/" )
	# logout


	@expose( template="web_console.common.templates.error" )
	def error( self, msg = None ):
		return util.getErrorTemplateArguments( msg )


	@expose( template="web_console.common.templates.error" )
	def accessdenied( self, *args, **kwargs ):
		raise AuthenticationException( "Access to resource denied" )
	# accessdenied


	# The default implementation of this is so damn verbose!
	def _cp_log_access( self ):
		tmpl = '%(h)s %(u)s "%(m)s %(r)s" %(p)s %(s)s (%(f)s)'

		paramStr = str ( cherrypy.request.params )
		paramLen = len( paramStr )
		if paramLen > 1024:
			paramStr = "<Parameters sized( %d ) are too large for logging>" \
					% paramLen

		try:
			username = cherrypy.request.user_name
			if not username:
				username = "-"
		except AttributeError:
			username = "-"

		s = tmpl % {'h': cherrypy.request.remoteHost,
					'u': username,
					'r': cherrypy.request.path,
					'p': paramStr,
					'f': cherrypy.request.headers.get('referer'),
					's': cherrypy.response.status[0:3],
					'm': cherrypy.request.method
 		}

		self.accesslog.info( s )
	# _cp_log_access


	# ------------------------------------------------------------------------------
	# Section: AsyncTask stuff
	# ------------------------------------------------------------------------------

	# For polling async tasks and returning JSON-able data structures
	@validate( validators = dict( id = validators.Int(),
								  blocking = validators.StringBool() ) )
	@ajax.expose
	def poll( self, id, blocking = False ):

		try:
			task = async_task.AsyncTask.get( id )
		except KeyError:
			# If a poll asks for an ID and it does not exist it is most likely
			# because it is already being/has been terminated due to an
			# interruption in the client.
			log.warning( "Unable to poll task ID %d. The task may have already "
						"been terminated.", id )
			raise ajax.Error( "Unable to poll task, the task may have already "
						"been terminated." )

		updates = task.poll( blocking )

		if updates:
			for state, data in updates:
				if state == "finished":
					task.terminate()
					break
			return dict( status = "updated", updates = updates )

		elif task.hasTimedOut():
			return dict( status = "timeout" )
		else:
			return dict( status = "nochange" )


	@identity.require( identity.not_anonymous() )
	@ajax.expose
	@validate( validators = dict( id = validators.Int() ) )
	def terminate( self, id ):

		try:
			async_task.AsyncTask.get( id ).terminate()

		# We may get terminate() calls from the client-side when the server-side
		# function call has already cleaned itself up.  That's OK.
		except KeyError:
			pass


	@identity.require( identity.not_anonymous() )
	@ajax.expose
	@validate( validators = dict( id = validators.Int() ) )
	def callExposed( self, type, method, onSuccess = None, **kw ):
		"""
		Calls a method on an instance of cluster.Exposed.  The 'type' parameter
		controls how the object is looked up, and each lookup method has its own
		arguments which are passed via **kw.  At the moment, only 'process' is
		understood.

		Args to be passed to the callback are also in **kw, but should have all
		been prefixed with __ to distinguish them from the arguments that
		qualify 'type'.
		"""

		c = cluster.cache.get()

		# We only know how to look up processes at the moment
		if type == "process":
			machine = c.getMachine( kw[ "machine" ] )
			if not machine:
				raise ajax.Error, "Unknown machine '%s'" % kw[ "machine" ]
			obj = machine.getProc( int( kw[ "pid" ] ) )

		callback = getattr( obj, method )

		# Marshal arguments to pass to the callback
		cbkw = {}
		for k, v in kw.items():
			if k.startswith( "__" ):
				cbkw[ k[2:] ] = v

		callback( **cbkw )
		if onSuccess:
			return onSuccess
		else:
			return
