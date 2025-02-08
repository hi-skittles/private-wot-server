import BWConfig

SHOULD_ACCEPT_UNKNOWN_USERS = \
	BWConfig.readBool( "billingSystem/shouldAcceptUnknownUsers", False )
SHOULD_REMEMBER_UNKNOWN_USERS = \
	BWConfig.readBool( "billingSystem/shouldRememberUnknownUsers", False )
ENTITY_TYPE_FOR_UNKNOWN_USERS = \
	BWConfig.readString( "billingSystem/entityTypeForUnknownUsers", "Account" )

print "shouldAcceptUnknownUsers =", SHOULD_ACCEPT_UNKNOWN_USERS
print "shouldRememberUnknownUsers =", SHOULD_REMEMBER_UNKNOWN_USERS
print "entityTypeForUnknownUsers =", ENTITY_TYPE_FOR_UNKNOWN_USERS

# db/billing_system_settings.py
