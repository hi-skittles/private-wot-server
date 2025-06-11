import ldap
import ldap.sasl
import logging

from turbogears import config 

import bwsetup; bwsetup.addPath( "../.." );

log = logging.getLogger( __name__ )


class LdapUtil( object ):
	"""
	Utility class to carry out LDAP related operations
	"""

	authMethod = None

	USE_TLS_NEVER = "NEVER"
	USE_TLS_TRY = "TRY"
	USE_TLS_ALWAYS = "ALWAYS"

	AUTH_METHOD_LOCAL = "LOCAL"
	AUTH_METHOD_LDAP= "LDAP"

	def __init__( self ):
		self.host = config.get( "identity.soldapprovider.host", "" )
		self.port = config.get( "identity.soldapprovider.port", 389 )
		
		if LdapUtil.isAuthByLdapEnabled() and not self.host:
			log.error( "identity.soldapprovider.host is not configured." )
		
		self.networkTimeOut = config.get(
				"identity.soldapprovider.network_time_out", 30 )
		self.operationTimeOut = config.get(
				"identity.soldapprovider.time_out", 60 )

		self.useTLS = config.get( "identity.soldapprovider.use_tls",
												LdapUtil.USE_TLS_NEVER ).upper()
		self.allowInvalidTlsCert = config.get( 
				"identity.soldapprovider.allow_invalid_tls_cert", True )				
		self.useSaslMd5 = config.get(
				"identity.soldapprovider.use_sasl_digest_md5" )

		self.adminUserDN = config.get( "identity.soldapprovider.user_dn" )
		self.adminPassword = config.get(
				"identity.soldapprovider.user_password" )

		self.baseDN = config.get( "identity.soldapprovider.basedn" )		
		self.userObjectClass = config.get(
				"identity.soldapprovider.userObjectClass", "person" )
		self.loginUserNameAttr = config.get(
				"identity.soldapprovider.loginUserNameAttr", "sAMAccountName" )

		self.serverUserNameAttr = config.get(
				"identity.soldapprovider.serverUserNameAttr", "sAMAccountName" )
		
		self.ldapUrl = "ldap://%s:%d" % ( self.host, self.port )

	# end __init__

	
	@classmethod
	def isAuthByLdapEnabled( cls ):
		return	LdapUtil.getAuthMethod() == LdapUtil.AUTH_METHOD_LDAP

	# end isAuthByLdapEnabled


	@classmethod
	def getAuthMethod( cls ):
		if LdapUtil.authMethod == None:
			LdapUtil.authMethod = config.get( "identity.auth_method", 
					LdapUtil.AUTH_METHOD_LOCAL ).upper()

		return LdapUtil.authMethod


	def validateLdapConfig( self ):
		"""
		Validate the LDAP configurations in WebConsole config file.
		"""

		ldapConnection =  self.bindLdapServerUsingAdmin()

		if ldapConnection:
			ldapConnection.unbind()
			return True
		else:
			log.error( "Failed in binding LDAP server using :%s",
				self.adminUserDN )
			return False 

	# end validateLdapConfig


	def getServerUserAttr( self, userName ):
		"""
		Get the server user attribute from LDAP server for given user name.
		"""

		userExists = False
		serverUserName = None

		ldapConnection = self.bindLdapServerUsingAdmin() 
		if not ldapConnection:
			log.error( "Failed in binding LDAP server using %s",
				self.adminUserDN )
				
			return ( userExists, serverUserName )

		userData = self.searchUser( ldapConnection, userName,
							[ self.serverUserNameAttr ] )
		if userData == None:
			log.error( "LDAP user with name %s may not exist.", userName )
			ldapConnection.unbind()
			return ( userExists, serverUserName )

		userExists = True

		if self.serverUserNameAttr in userData[1]:
			serverUserName = userData[1][ self.serverUserNameAttr ][0]

		ldapConnection.unbind()

		return ( userExists, serverUserName )

	# end getServerUserAttr


	def authenticateUser( self, userName, password ):
		"""
		Authenticate user credentials against LDAP server
		"""

		# search the user and get the DN
		ldapConnection = self.bindLdapServerUsingAdmin() 
		if not ldapConnection:
			log.error( "Failed in binding LDAP server using %s",
				self.adminUserDN )
				
			return False

		userData = self.searchUser( ldapConnection, userName,
							[ self.loginUserNameAttr ] )
		if userData == None:
			ldapConnection.unbind()
			return False

		userDN = userData[0]
		bindResult = False
		
		if self.useSaslMd5:
			bindResult = self.doSaslBind( ldapConnection, userName, password )
		else:
			bindResult = self.doSimpleBind( ldapConnection, userDN, password )
			
		ldapConnection.unbind()
		
		return bindResult 

	# end authenticateUser


	def searchUser( self, ldapConnection, userName, attrList ):
		"""
		Search user from LDAP server by given user name. Return the LDAP data
		of the first matched item, which is a list of two tiems: user DN
		and a attr:value dictionary.
		"""

		filterStr = "(&(objectClass=%s)(%s=%s))" % \
					( self.userObjectClass, self.loginUserNameAttr, userName )
		try:
			userData = ldapConnection.search_s( self.baseDN,
					ldap.SCOPE_SUBTREE, filterStr, attrList )
		except Exception, ex:
			log.error( "Failed searching user, error: %s", ex )
			return None

		# some useless entry with DN=None may be returned, here we need check
		# whether DN is None
		if (len( userData ) == 0) or userData[0][0] == None:
			log.warning( "No such LDAP user: %s" % userName )
			return None

		return userData[0] 

	# end searchUser


	def bindLdapServerUsingAdmin( self ):
		"""
		Bind to LDAP server with the user information configured in WebConsole
		config file. Return the LDAP connection if the bind is successful,
		otherwise return None
		"""

		ldapConnection = ldap.initialize( self.ldapUrl )

		ldapConnection.set_option( ldap.OPT_NETWORK_TIMEOUT,
				self.networkTimeOut )
		ldapConnection.set_option( ldap.OPT_TIMEOUT,
				self.operationTimeOut )

		# special setting to work with Windows AD
		ldapConnection.set_option( ldap.OPT_REFERRALS, 0 )

		# To work with LDAPv3
		ldapConnection.protocol_version = 3

		# start TLS if use TLS is enabled
		if self.useTLS == LdapUtil.USE_TLS_TRY or \
				self.useTLS == LdapUtil.USE_TLS_ALWAYS:

			if self.allowInvalidTlsCert:
				ldap.set_option( ldap.OPT_X_TLS_REQUIRE_CERT,
					ldap.OPT_X_TLS_NEVER )

			try:
				ldapConnection.start_tls_s()
			except Exception, ex:
				log.error( "Failed to start TLS with LDAP server:%s, error:%s",
						self.host, ex )
						
				if self.useTLS == LdapUtil.USE_TLS_ALWAYS:
					# if use TLS is MUST, return as error, otherwise continue
					return None

		if self.doBind( ldapConnection, self.adminUserDN, self.adminPassword ):
			return ldapConnection

		return None 

	# end bindLdapServerUsingAdmin 


	def doBind( self, ldapConnection, userDN, password ):
		"""
		Do a bind job on a ldapConnection with given user information
		"""

		if self.useSaslMd5:
			return self.doSaslBind(  ldapConnection, userDN, password  )
		else:
			return self.doSimpleBind( ldapConnection, userDN, password )

	# end doBind


	def doSaslBind( self, ldapConnection, userName, password ):
		"""
		Do a SASL bind on a ldapConnection with given user information. Only
		user name can be accepted when doing SASL bind.
		"""

		try:
			# when binding using SASL, the userName can only be username
			# here we try to parse out the user name if userName happens to
			# be in the format domain.name\username
			userName = userName.split("\\")[-1]
					
			authTokens = ldap.sasl.digest_md5( userName, password )

			ldapConnection.sasl_interactive_bind_s( "", authTokens )
		except Exception, ex:
			log.error( "Failed to bind to LDAP server:%s using account:%s, "
					"error: %s", self.host, userName, ex )
			return False 

		return True

	# end doSaslBind


	def doSimpleBind( self, ldapConnection, userDN, password ):
		"""
		Do a simple bind on a ldapConnection with given user information. Only
		user DN can be accepted when doing simple bind.
		"""

		try:
			ldapConnection.simple_bind_s( userDN, password )
		except Exception, ex:
			log.error( "Failed to bind to LDAP server:%s using account:%s, "
					"error: %s", self.host, userDN, ex )
			return False 

		return True

	# end doSimpleBind

# end class LdapUtil

