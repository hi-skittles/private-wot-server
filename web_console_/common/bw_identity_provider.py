import ldap
import logging

from turbogears import config, identity
from turbogears.identity.soprovider import SqlObjectIdentityProvider


import bwsetup; bwsetup.addPath( "../.." );

from ldap_util import LdapUtil

log = logging.getLogger( __name__ )


class BwIdentityProvider( SqlObjectIdentityProvider ):
	"""
	IdentityProvider of BigWorld, supports LDAP authentication.
	"""

	def __init__( self ):
		super( BwIdentityProvider, self ).__init__()
		
		self.ldapUtil = LdapUtil()
		self.authByLdap = LdapUtil.isAuthByLdapEnabled()
		


	# Override the method of SqlObjectIdentityProvider
	def validate_password( self, user, userName, password ):

		# Use original password stored in local DB to authenticate if
		# authentication by LDAP is not enabled or the user is the default admin
		if userName == "admin" or not self.authByLdap:
			if not password:
				identity.set_identity_errors("Password was empty")	
				return False

			return super( BwIdentityProvider, self ).validate_password( user,
					userName, password )

		if not self.ldapUtil.authenticateUser( userName, password ):
			errorStr = "Failed to authenticate %s with LDAP" % userName
			log.error( errorStr )
			identity.set_identity_errors( errorStr )	

			return False 

		return True
