

import logging
import simplejson as json
import cherrypy
import turbogears.identity
from turbogears.identity.conditions import Predicate, IdentityPredicateHelper
import sys
import os.path

import bwsetup; bwsetup.addPath( "../.." )
from pycommon.exceptions import AuthenticationException, AuthorisationException
from web_console.common.module import Module
from web_console.common.authorisation_filter import AuthorisationFilter

log = logging.getLogger( __name__ )


class Permission( Predicate, IdentityPredicateHelper ):
	"""
	Typical usage:

		@identity.require( Permission( "view", "modify" ) )

	"""

	# group name which has all rights defined (but not necessarily granted)
	# this is used to sanity check that a permission exists when declared
	# in a decorator
	ALL_RIGHTS_GROUP = "admin"

	GROUP_WITH_NO_PERMISSIONS_IS_FATAL = False

	# Maps group names to a dict of permissions for that group
	GroupRights = {}

	# Maps WebConsole resources (terminal URL paths) to the list of permissions
	# required to access that resource.
	PermissionsByUrl = {}


	def __init__( self, *rights ):

		assert self.GroupRights
		assert rights

		self.rights = set()
		for right in rights:
			if right not in self.GroupRights[self.ALL_RIGHTS_GROUP]:
				raise Exception( "Non-existant right '%s'" % right )
			self.rights.add( right )
	# __init__


	@classmethod
	def initRights( self ):
		""" Initialises the permissions/rights system from configuration. """

		filename = turbogears.config.get(
			'web_console.authorisation.config', 'users.json' )

		if not os.path.isfile( filename ):
			filename = os.path.join(
				os.path.dirname( os.path.abspath( sys.argv[ 0 ] ) ),
				filename )

		self.GROUP_CONFIG_FILE = filename
		try:
			stream = open( filename )
			self.GroupRights = json.load( stream )
		except Exception, ex:
			log.warning( "Failed to init permissions from file '%s': %s",
				filename, ex )
			raise
		log.info( "Permissions loaded from file '%s'", filename )

		allRights = self.GroupRights[self.ALL_RIGHTS_GROUP]
		if not allRights:
			raise Exception(
				"Permission config file '%s' missing '%s' group. "
				"This group is required to define all available permissions." %
				filename, self.ALL_RIGHTS_GROUP
			)

		log.info( "Available rights: %r", allRights.keys() )
		for group_name, rightsDict in self.GroupRights.items():
			# if rightsDict is allRights:
			# 	continue
			log.info(
				"Group '%s' has user rights: %r, other rights: %r", group_name,
				[r for r in sorted( rightsDict.keys() ) if rightsDict[r][0]],
				[r for r in sorted( rightsDict.keys() ) if rightsDict[r][1]]
			)
	# _initRights


	@classmethod
	def getPermissionsList( self ):
		""" Returns the set of defined permissions as a list in display order. """
		permissionsList = self.GroupRights[self.ALL_RIGHTS_GROUP].keys()
		return sorted( permissionsList, reverse = True )
	# getPermissionsList


	@classmethod
	def getPermissionsByMethod( self ):
		""" Returns dict of all @expose'd methods that have a Permission predicate,
		which maps method name to the tuple of permissions that method requires.

		Uses reflection to traverse graph of @expose'd methods of all L{Module}s
		that also declare a L{Permission} L{Predicate}.

		Exploits the fact that the turbogears "@expose" and "@identity.require"
		decorators add properties "exposed" and "_require" (respectively) to the
		method they decorate.

		Dict returned maps each L{String} resource URL to the tuple of String rights
		required to access that resource.

		Currently asserts on encountering a method name/resource relative URL
		fragment that has already been defined. Could convert to using
		path-qualified or absolute URLs, but the downside would be that HTML
		links declared without the qualifying path(s) would no longer be matched.

		In practise, relative URLs are working fine for now.
		"""
		if self.PermissionsByUrl:
			return self.PermissionsByUrl

		from inspect import getmembers, ismethod
		permissionsByMethod = {}
		moduleList = Module.all()

		log.info( "Discovering permissions-protected methods" )
		for module in moduleList:
			methods_list = [m for m in getmembers( module, ismethod )]
			for name, member in methods_list:
				# is method @exposed?
				if callable( member ) and hasattr( member, 'exposed' ):
					# did method have @identity.require?
					if hasattr( member, '_require' ):
						# does the Predicate in identity.require look
						# like a Permission instance?
						if hasattr( member._require, 'rights' ):
							# OK, it's a Permission or Permission-like object
							# print module.__class__.__name__ + "::" + name
							rights = tuple( member._require.rights )
							assert not permissionsByMethod.get( name ), \
								"Duplicate method/resource '%s' in %s" % \
								(name, module.__class__)
							permissionsByMethod[name] = rights

		# if log.isEnabledFor( logging.DEBUG ):
		# 	log.debug( "permissions by url:\n%s",
		# 		json.dumps( permissionsByMethod, indent = 4 ) )

		self.PermissionsByUrl = permissionsByMethod
		return permissionsByMethod
	# getPermissionsByMethod


	@classmethod
	def getRights( self, groups, asOwner=True ):
		""" Returns the set of rights for the provided groups iterable. """

		assert len( groups )
		assert isinstance( asOwner, bool )

		rights = set()
		selfOrOther = int( not asOwner ) # ie: 0 or 1

		for group_name in groups:
			group_rights = self.GroupRights.get( group_name )
			if not group_rights:
				if self.GROUP_WITH_NO_PERMISSIONS_IS_FATAL:
					raise AuthorisationException(
						"Non-existent group '%s'" % group_name )
				else:
					log.debug( "group '%s' has no rights defined", group_name )
					continue

			for right in group_rights:
				if group_rights[right][selfOrOther]:
					rights.add( right )

		return rights
	# getRights


	def eval_with_object( self, identity, errors = None ):
		""" Overriden from L{Predicate}. """

		# Equivalent to identity.not_anonymous()
		if identity.anonymous:
			raise AuthenticationException( "Anonymous access denied" )

		actingServeruser = getattr( cherrypy.request.identity,
			AuthorisationFilter.ACTING_USER_KEY, None )

		isOwnServer = (actingServeruser == None)

		if not self.canAccess( identity.groups, isOwnServer ):
			log.info( "Access to resource is denied: %s", cherrypy.request.path )
			raise AuthorisationException(
				"You don't have sufficient permissions for this resource" )

		log.info( "Access to resource is granted: %s", cherrypy.request.path )
		return True
	# eval_with_object


	def canAccess( self, groups, asOwner=None ):
		""" Returns True if the given group iterable satisfies this L{Permission},
		False otherwise. """

		assert len( groups )
		# assert isinstance( asOwner, bool )

		if asOwner is None:
			actingServeruser = getattr( cherrypy.request.identity,
				AuthorisationFilter.ACTING_USER_KEY, None )
			asOwner = (actingServeruser == None)

		rights = self.getRights( groups, asOwner )
		log.debug( "Rights for group %s: %r", list( groups ), list( rights ) )
		log.debug( "Required rights are %r for resource: %s", list( self.rights ),
			cherrypy.request.path )

		missingRights = self.rights - rights
		if missingRights:
			log.debug( "Access denied, missing rights: %r", list( missingRights ) )
			return False

		return True
	# canAccess

# end class Permission

# authorisation.py

