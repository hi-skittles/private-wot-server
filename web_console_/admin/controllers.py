# Standard Python includes
import logging

# Turbogears modules
from turbogears import expose, identity, redirect, validate, validators
from turbogears import config, scheduler
from turbogears.identity import soprovider

# Other BigWorld python modules
import bwsetup; bwsetup.addPath( "../.." )
from pycommon import cluster
from pycommon import bw_profile
from pycommon.exceptions import ServerStateException
from web_console.common import module, model, util
from web_console.common.authorisation import Permission
from web_console.common.ldap_util import LdapUtil

log = logging.getLogger( __name__ )
DUMP_TIME_DEFAULT = 10
DUMP_TIME_WARNING = 15

class LdapUserNotExists( Exception ):
	""" Raised when the LDAP user of given name doesn't exist. """

	def __init__( self, userName ):
		Exception.__init__( self, userName )
		self.userName = userName
		

	def __str__( self ):
		return self.userName

# end class LdapUserNotExists 


class ServerUserNotExists( Exception ):
	""" Raised when the LDAP user exists but server user attribute not. """

	def __init__( self, userName ):
		Exception.__init__( self, userName )
		self.userName = userName
		

	def __str__( self ):
		return self.userName

# end class ServerUserNotExists 


class Admin( module.Module ):

	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )
		self.addPage( "Users", "users" )
		self.addPage( "Groups", "groups" )
		self.addPage( "Add User", "edit?action=add" )
		self.addPage( "Flush Users", "flush" )
		self.addPage( "Self Profiling", "profiling" )
		self.addPage( "Help", "help" )		

		self.ldapUtil = LdapUtil()


	@identity.require( identity.in_group( "admin" ) )
	@expose( template = "admin.templates.list" )
	def users( self ):

		users = self.getUserList()
		groups = self.getGroupList()

		# Generate actions for each user
		options = {}
		for user in users:
			opt = util.ActionMenuOptions()

			opt.addRedirect( "Edit", "edit",
							 params = dict( username = user.user_name,
											action = "edit" ) )

			if str( user.user_name ) != "admin":
				opt.addRedirect( "Delete", "delete",
							 params = dict( username = user.user_name ) )

			options[ user ] = opt

		return dict( users = users, options = options, groups = groups,
				authByLdapEnabled = LdapUtil.isAuthByLdapEnabled() )
	# users


	@identity.require( identity.in_group( "admin" ) )
	@expose( template = "admin.templates.groups" )
	def groups( self ):
		groups = self.getGroupList()
		permissions = Permission.getPermissionsList()
		return dict(
			groups = groups,
			permissions = permissions,
			groupPermissions = Permission.GroupRights
		)
	# groups


	@identity.require( identity.in_group( "admin" ) )
	@validate( validators = dict( id = validators.Int() ) )
	@expose( template = "admin.templates.edit" )
	@util.unicodeToStr
	def edit( self, action, username = None, pass1 = None, pass2 = None,
			  serveruser = None, id = None, group = None ):

		groups = self.getGroupList()

		authByLdapEnabled = self.ldapUtil.isAuthByLdapEnabled() 

		if action == "add" and username is None:
			# show add new user page
			return dict( user = None, groups = groups, 
					authByLdapEnabled = authByLdapEnabled )

		if action == "edit" and id is None:
			# show edit user page
			user = model.User.byName( username )
			return dict( user = user, groups = groups, 
					authByLdapEnabled = authByLdapEnabled )

		# else we are creating/updating a user
		isAdmin = False
		existingUser = None
		if id is not None:
			existingUser = model.User.get( id )
			isAdmin = existingUser and existingUser.isAdmin()

		isDefaultAdmin = ( username == "admin" )

		# Verify
		# verify user name
		if not username:
			return self.error( "'username' must be defined" )

		if action == "add":
			existingUser = model.User.byName( username )
			if existingUser:
				return self.error( "User '%s' already exists" % username )

		elif action == "edit":
			if not existingUser:
				return self.error( "User named '%d' doesn't exist" % id )

			# Avoid name conflicts when editing user
			userByName = model.User.byName( username )
			if userByName and userByName.id != id:
				return self.error( "User '%s' already exists" % username )

		if authByLdapEnabled and not isDefaultAdmin:
			ldapUserExists, serveruser = \
					self.ldapUtil.getServerUserAttr( username )
			if not ldapUserExists:
				errStr = """User '%s' does not exist on LDAP server. Please
							check your input and LDAP setting, and try
							again.""" % username

				return self.error( errStr )

		# verify password
		if authByLdapEnabled and not isDefaultAdmin:
			pass1 = ""
		elif not pass1:
			return self.error( "Passwords cannot be empty" )
		elif pass1 != pass2:
			return self.error( "Passwords did not match" )

		# verify group and server user
		if isDefaultAdmin:
			# when editing admin, this field will be hidden on UI
			group = "admin"
		else:
			# check group
			if not group:
				return self.error( "A group must be provided" )

			# check server user
			if not serveruser:
				if authByLdapEnabled:
					errStr = """User '%s' does not have server user attribute
								on LDAP server. Please check your LDAP setting
								and try again.""" % username
				else:
					errStr = "'Server User' must be defined."

				return self.error( errStr )

			c = cluster.cache.get()
			serverusers = c.getAllUsers()

			if serveruser not in [user.name for user in serverusers]:
				errStr = """Server user '%s' does not exist or does not
							have a valid ~/.bwmachined.conf.  Click 'Flush User
							Mappings' to refresh user mappings for all
							bwmachined processes, and try again."""
				return self.error( errStr % serveruser )

		# groupObj = list( model.User.select( model.User.q.user_name == username ) )[0]
		try:
			groupObj = model.Group.by_group_name( group )
		except:
			return self.error( "No group with name '%s'" % group )

		if action == "add":
			newUser = model.User(
				user_name = username,
				password = pass1,
				serveruser = serveruser )
			newUser.addGroup( groupObj )

		elif action == "edit":
			existingUser.user_name = username
			existingUser.serveruser = serveruser
			for g in existingUser.groups:
				existingUser.removeGroup( g )
			existingUser.addGroup( groupObj )
			if pass1:
				existingUser.password = pass1

		raise redirect( "users" )
	# edit


	@identity.require( identity.in_group( "admin" ) )
	@expose( template = "admin.templates.flush" )
	def flush( self, confirmed = False ):

		# Flush user cache of all bwmachined in the network so that new
		# users in the network will be recognised.
		if not confirmed:
			return dict( )
		else:
			c = cluster.cache.get()
			ms = c.getMachines()
			for m in ms:
				m.flushMappings()

			raise redirect( "users" )


	@identity.require( identity.in_group( "admin" ) )
	@validate( validators = dict( confirmed = validators.StringBool() ) )
	@expose( template = "admin.templates.delete" )
	@util.unicodeToStr
	def delete( self, username = None, confirmed = False ):

		if not confirmed:
			return dict( username = username )
		else:
			rec = model.User.byName( username )
			rec.destroySelf()
			raise redirect( "users" )


	@identity.require( identity.in_group( "admin" ) )
	@expose( "json" )
	def queryLdapUser( self, userName ):
		ldapUserExists, serverUser = self.ldapUtil.getServerUserAttr( userName )

		if not ldapUserExists:
			raise LdapUserNotExists( userName )
		elif not serverUser:
			raise ServerUserNotExists( userName )

		return dict( serverUser = serverUser )


	@identity.require( identity.in_group( "admin" ) )
	@expose()
	def index( self, **kw ):
		raise redirect( "users" )


	@identity.require( identity.not_anonymous() )
	@expose( template="web_console.common.templates.error" )
	def error( self, msg ):
		return util.getErrorTemplateArguments( msg )


	@identity.require( identity.in_group( "admin" ) )
	@expose( template="admin.templates.profiling" )
	def profiling( self ):
		return dict( isAvailable = bw_profile.isAvailable(),
				default_dump_time = DUMP_TIME_DEFAULT,
				warning_dump_time = DUMP_TIME_WARNING )
	# profiling


	@identity.require( identity.in_group( "admin" ) )
	@expose( "json" )
	def profilingStatus( self ):
		return bw_profile.getJsonDumpStatusInfo()
	# bwProfilingStatus


	@identity.require( identity.in_group( "admin" ) )
	@expose( "json" )
	def getJsonOutputFilePath( self ):
		return bw_profile.getJsonOutputFilePath()
	# getJsonDumpFilePath


	@identity.require( identity.in_group( "admin" ) )
	@expose( "json" )
	def profilingStartStop( self, dump_time ):
		if not bw_profile.isAvailable():
			# Theoretically this function should not be called when not
			# available but this is a preventative measure just in case.
			log.error( "profilingStartStop: Invalid call. bw_profile is not "
				"available" )
			return dict()

		try:
			if not bw_profile.isEnabled():
				log.info( "Starting WebConsole self profiling" )
				bw_profile.enable( 1 )

				try:
					bw_profile.setJsonDumpCount( int( dump_time ) )
				except (TypeError, ValueError):
					return dict( alertType = "Error",
						message = "Dump time is not a valid integer." )
				bw_profile.startJsonDump()
				bw_profile.tick()

				self.profilingTask = scheduler.add_interval_task(
					processmethod = scheduler.method.sequential,
					action = bw_profile.tick,
					taskname = 'bw_profile.tick',
					interval = 1 )

				return dict( alertType="Info",
					message = "WebConsole self profiling started" )
			else:
				log.info( "Stopping WebConsole self profiling" )

				scheduler.cancel( self.profilingTask )
				bw_profile.enable( 0 )
				# One more forced manual tick required
				bw_profile.tick()

				return dict( alertType="Info",
					message = "WebConsole self profiling stopped." )
		except Exception, ex:
			log.error( "profilingStartStop: An error occurred: %s", str( ex ) )
			raise
	# profilingStartStop


	def getGroupList( self ):
		""" Returns a list of all L{Group}s sorted by least to most permissions,
			with the 'admin' group special-cased to be last. """

		groups = list( model.Group.select() )
		def getPermissionsCount( group ):
			if group.group_name == "admin":
				return 999999
			return 1.0 * len( Permission.getRights( [group.group_name], True ) ) \
				+ 1.1 * len( Permission.getRights( [group.group_name], False ) )

		groups.sort( key = getPermissionsCount )
		return groups
	# getGroupList


	def getUserList( self ):
		return sorted( list( model.User.select() ), key = lambda u: u.user_name )
	# getUserList
