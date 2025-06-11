
import logging
from cherrypy import request, response
from cherrypy.filters.basefilter import BaseFilter
import turbogears
from turbogears import identity

import cgi
from urlparse import urlsplit, urlunsplit

from pycommon import cluster
from pycommon.exceptions import AuthenticationException, AuthorisationException

log = logging.getLogger( __name__ )


class AuthorisationFilter( BaseFilter ):
	"""
	CherryPy filter that inserts into the HTTP request lifecycle to implement
	the core of WebConsole's authorisation framework.

	Authorisation can be disabled or enabled on a per-url basis by setting the
	web application config property `web_console.authorisation.on` to False/True.
	See the L{shouldApplyFilter} method for further details.
	"""

	# name of the attribute that will be set o
	ACTING_USER_KEY = 'acting_user'

	# cached version of output from L{getPermissionsCss}
	PERMISSIONS_CSS = ""

	# default style to apply to page elements that a user does not
	# possess permissions to access; see L{getPermissionsCss}
	PERMISSIONS_CSS_STYLE = "display: none"


	def __init__( self ):
		log.info( "%s loaded", self.__class__.__name__ )

		# init cached CSS
		self.getPermissionsCss()
	# __init__


	def before_request_body( self ):
		"""
		Intercepts & arbitrates propagation of the `user` param for the purposes
		of determining the currently acting serveruser. The method employed here
		essentially uses the Referer header and the CGI param `user` to determine
		acting serveruser.

		The basic method is as follows:
		* If a `user` param was given, nothing happens; the request proceeds normally.
		* If no `user` param was given, and there is a `user` param in the URL in
		the Referer header, it is taken to be the currently acting serveruser, and
		a redirect issued that includes the user param.

		The redirect can be disabled on a per-URL basis in the config by setting the
		`web_console.authorisation.propagateUser` property to False (such as in the
		case for spaceviewer assets, which are reverse-proxied to serviceapps).
		"""
		if request.path == '/auth/permissions.css':
			return self.staticPermissionsCss()

		if not self.shouldApplyFilter():
			return

		log.debug( "before_request_body: %s, %r", request.path, request.params )

		# self.rewriteUserPathinfo()

		# don't apply to root url, just let login logic handle it
		if request.path == '/':
			return

		# don't overwrite explicit 'user=xxx'
		if 'user' in request.params:
			return

		if self.ACTING_USER_KEY in request.params:
			log.warning(
				"URL contains reserved param '%s': %s",
				self.ACTING_USER_KEY, request.path  )
			return

		referer = request.headers.get( 'Referer', None )
		log.debug( "Referer: %s", referer )
		if not referer:
			return

		# parse into components:
		#   "<scheme>://<netloc>/<path>?<query>#<fragment>"
		(scheme, netloc, path, query, fragment) = urlsplit( referer )

		queryDict = cgi.parse_qs( query, keep_blank_values=True )

		referedUser = queryDict.get( 'user', [None] )[0]
		log.debug( "referedUser: %s", referedUser )
		if not referedUser:
			# no user param in referer, therefore assume user is acting as self
			# the rule is, if a user is acting as a serveruser other than their
			# own, the URL will contain a 'user' param.
			return

		log.debug( "adding refered user '%s' to params", referedUser )
		request.params['user'] = referedUser

		# no need to redirect JSON requests
		if 'application/json' in request.headers['Accept']:
			return

		if not turbogears.config.get( 'web_console.authorisation.propagateUser', True ):
			return

		log.info( "redirecting after adding acting user '%s'", referedUser )
		turbogears.redirect( request.path, request.params )

	# before_request_body


	def before_main( self ):
		"""
		Determines which serveruser the current user (identity) is attempting
		to access. Note that this filter must run *before* the turbogears filter.
		"""

		if not self.shouldApplyFilter():
			return

		if not identity.current.user:
			return

		log.debug( "before_main: %s, %r", request.path, request.params )

		actualUser = identity.current.user.user_name
		currentActingUser = getattr( request, self.ACTING_USER_KEY, None )
		intendedUser = request.params.get( 'user', currentActingUser )

		log.debug(
			"actualUser=%s, currentActingUser=%s, intendedUser=%s",
			actualUser, currentActingUser, intendedUser )

		# unconditionally remove 'user' param from params
		# to prevent existing controller methods from using it -
		# they should all go through getServerUsername
		if request.params.pop( 'user', None ):
			log.debug( "removed param 'user'" )

		# update identity.intendedUser
		if intendedUser and intendedUser != actualUser:
			try:
				# check that serveruser exists
				user = cluster.cache.get().getUser( intendedUser )

				# an unknown user should raise an exception; assert just in case
				assert user

				# Actual permission checking is done at the resource level
				# through the identity.require decorator.

				setattr( identity.current, self.ACTING_USER_KEY, intendedUser )
				log.info(
					"User '%s' is now acting as serveruser '%s' for resource: %s",
					actualUser, intendedUser, request.path
				)
			except Exception, ex:
				log.warning( "No known user '%s': %s", intendedUser, ex )
				if 'application/json' in request.headers['Accept']:
					raise AuthorisationException(
						"No known user '%s'" % intendedUser )
				else:
					turbogears.redirect( '/error',
						{ 'msg': "Unknown server user '%s'" % intendedUser } )
		else:
			log.debug( "User '%s' acting as themselves", actualUser )
			setattr( identity.current, self.ACTING_USER_KEY, None )

	# before_main


	#  *** commented out as not currently used ***
	#
	# ACTING_USER_URI = '/as/'
	#
	# def rewriteUserPathinfo( self ):
	# 	"""
	# 	Rewrites URLs of form '/<ACTING_USER_URI><user>/rest/of/url' to
	# 	'/rest/of/url' and sets request.params['user'] to '<user>'.
	# 	"""

	# 	if 'user' in request.params:
	# 		# explicit 'user' param takes precedence over path
	# 		return

	# 	path = request.path
	# 	pathIndex = path.find( self.ACTING_USER_URI )
	# 	if pathIndex == -1:
	# 		return

	# 	pathIndex += len( self.ACTING_USER_URI )
	# 	userEndIndex = path.find( '/', pathIndex )
	# 	if userEndIndex == -1:
	# 		log.warning( 'incomplete/malformed URL?: %s', request.path )
	# 		return

	# 	user = path[pathIndex:userEndIndex]
	# 	path = path[userEndIndex:]

	# 	log.info(
	# 		"rewriting URL: %s --> %s, and adding param user='%s'",
	# 		request.path, path, user )

	# 	request.path = path
	# 	request.params['user'] = user
	# # rewriteUserPathinfo


	def shouldApplyFilter( self ):
		"""
		Returns True if this filter should apply to the currently-requested
		resource, False otherwise.
		"""

		getConfig = turbogears.config.get

		# don't apply to static assets
		if getConfig( 'static_filter.on', False ):
			log.debug( 'not applying filter, static_filter.on=True: %s', request.path )
			return False

		# this filter requires identity enabled for this resource
		if not getConfig( 'identity.on', False ):
			log.debug( 'not applying filter, identity.on=False: %s', request.path )
			return False

		if getConfig( 'web_console.authorisation.on', False ):
			log.debug( 'applying filter, web_console.authorisation.on=True: %s', request.path )
			return True

		log.debug( 'not applying filter, web_console.authorisation.on=False: %s', request.path )
		return False
	# shouldApplyFilter


	def staticPermissionsCss( self ):
		"""
		Sets response body and headers to serve the output of L{getPermissionsCss}.
		"""
		css = self.getPermissionsCss()
		response.body = css
		response.headers['Content-Type'] = 'text/css'
		response.headers['Content-Length'] = len( css )

		# skip processing of request body & skip going through turbogears
		request.execute_main = False
	# staticPermissionsCss


	@classmethod
	def getPermissionsCss( self ):
		"""
		Returns a (String) block of CSS that applies the given styles to
		page elements that a user would not have permissions to access.
		"""

		if self.PERMISSIONS_CSS:
			return self.PERMISSIONS_CSS

		from web_console.common.authorisation import Permission
		permissionsByMethod = Permission.getPermissionsByMethod()

		# create some css based on available permissions info

		css = ""

		# rules for hiding links based on owner permissions
		for path, rights in permissionsByMethod.items():
			for right in rights:
				css += "html.acting-as-owner:not( .can-%s ) a[href *= '%s'],\n" \
					% (right, path)
				css += "html.acting-as-owner:not( .can-%s ) form[action *= '%s'],\n" \
					% (right, path)

		# rules for hiding links based on other permissions
		for path, rights in permissionsByMethod.items():
			for right in rights:
				css += "html.acting-as-other:not( .can-%s ) a[href *= '%s'],\n" \
					% (right, path)
				css += "html.acting-as-other:not( .can-%s ) form[action *= '%s'],\n" \
					% (right, path)

		css += ".access-denied { %s }\n\n" % self.PERMISSIONS_CSS_STYLE

		self.PERMISSIONS_CSS = css
		return css
	# getPermissionsCss


# end class AuthorisationFilter

# authorisation_filter.py

