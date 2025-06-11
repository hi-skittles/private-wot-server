class DATABASE_CONST:
	DB_PRIMARY_DATABASE_NAME = 'player_data_dev1'  # player table name
	DB_DO_EXTRA_DEBUG = True  # set this to false if you don't want to see a bunch of debug messages
	DB_IS_DEV = True
	#   #
	LOGIN_DB_DATABASE_NAME = DB_PRIMARY_DATABASE_NAME
	LOGIN_DB_PTABLE_NAME = 'accounts0'
	LOGIN_DB_DTABLE_NAME = 'accounts1'
	LOGIN_DB_TABLE_NAME = LOGIN_DB_DTABLE_NAME if DB_IS_DEV else LOGIN_DB_PTABLE_NAME
	LOGIN_DB_DO_EXTRA_DEBUG = True


class BASEAPP_CONST:
	BA_DO_DEBUG = True
	MAX_ONLINE_ACCOUNTS = 1000  # maximum number of online accounts

SELL_PRICE_FACTOR = 0.5