import BWConfig

SHOULD_ACCEPT_UNKNOWN_USERS = \
	BWConfig.readBool("billingSystem/shouldAcceptUnknownUsers", False)
SHOULD_REMEMBER_UNKNOWN_USERS = \
	BWConfig.readBool("billingSystem/shouldRememberUnknownUsers", False)
ENTITY_TYPE_FOR_UNKNOWN_USERS = \
	BWConfig.readString("billingSystem/entityTypeForUnknownUsers", "Login")

# db/billing_system_settings.py
