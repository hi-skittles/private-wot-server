from sqlobject import *
from datetime import datetime
import md5
import re

import logging
log = logging.getLogger( __name__ )

try:
	import sqlite
except ImportError:
	import sqlite3 as sqlite

try:
	import MySQLdb
except ImportError:
	print "MySQLdb is not installed"

import turbogears
from turbogears.database import PackageHub
from turbogears import identity

import authorisation as auth
from authorisation_filter import AuthorisationFilter
from ldap_util import LdapUtil

DB_TYPE_MYSQL = "mysql"
DB_TYPE_SQLITE = "sqlite"
SUPPORTED_DBS = (DB_TYPE_MYSQL, DB_TYPE_SQLITE)
NOTRANS_PREFIX = "notrans_"

hub = PackageHub( "web_console" )
__connection__ = hub

"""
Notes when using SQLObject:
===============================
In SQLObject 0.7.3, it did some very bad things when you have foreign key
attributes which ended in "id". For example, with an attribute named
"uid", SQLObject 0.7.3 would do the following:

- Create a table named "uid"
- Create an object attribute named "u" which returns the object being pointed
  to. This attribute also used for assigning objects.
  Example: object.u = User("hello")
- Create an object attribute named "uid" which returned the primary key of the
  object being pointed to. This is meant to be used in queries.

In SQLObject 0.8.0, the following happens:
- Create a table named "uid_id"
- Create an object attribute named "uid" which returned the object being
  pointed to.
- Create an object attribute name "uidID" which returned the primary key of the
  object being pointed to.

The different behaviour causes problems when moving from SQLObject 0.7.3 to 0.8.
This means we should follow this rule: Foreign key attributes must not end in
the characters "id", regardless of case. The behaviour for both SQLObjects
when we have foreign keys not ending in "id" is equivalent to 0.8's behaviour.


How to use SQLObject foreign keys
=================================
Here are examples for a class called "Obj" which has an attribute of "user"
which in turn is a foreign key to a "User" class:

bobUser = User("bob")
- Assigning: obj.user = bobUser
- Querying: obj.select( Obj.q.userID == bobUser.q.id )
- Accessing: ourUser = obj.user
- Creating: obj = Obj( user=bobUser )
"""

class DictSQLObjectType( declarative.DeclarativeMeta ):
	"""
	Metaclass to add each subclass of DictSQLObject to a list.  We use this list
	to enforce correct database schemas in enforceSchemas().
	"""

	s_classes = []

	def __init__( cls, *args, **kw ):
		declarative.DeclarativeMeta.__init__( cls, *args, **kw )
		DictSQLObjectType.s_classes.append( cls )


def getSQLiteTableColumnDict( cursor, tablename ):
	cursor.execute( "PRAGMA table_info( %s );" % tablename )
	return dict( [x[1:3] for x in cursor.fetchall()] )


def getMySQLTableColumnDict( cursor, tablename ):
	cursor.execute( "describe %s;" % tablename )
	return dict( [x[:2] for x in cursor.fetchall()] )


class DictSQLObject( SQLObject ):
	"""
	Fairly trivial subclassing of SQLObject with operators defined so that
	calling dict() on an instance of this class will work as you'd expect.
	"""

 	__metaclass__ = DictSQLObjectType

	def keys( self ):
		return self.sqlmeta.columns.keys()

	def __len__( self ):
		return len( self.sqlmeta.columns )

	def __getitem__( self, key ):
		return getattr( self, key )

	def __iter__( self ):
		return ( (c, getattr( self, c )) for c in \
			self.sqlmeta.columns.iterkeys() )


	@staticmethod
	def _getDBType( dbURI ):
		""" Extracts (and checks) the database type from a dburi that is in the
		format "[notrans_]type://...", ignoring optional [notrans_] sqlobject
		prefixes. """
		dbTypeStartPos = 0

		if dbURI.startswith( NOTRANS_PREFIX ):
			dbTypeStartPos = len( NOTRANS_PREFIX )

		dbTypeEndPos = dbURI.find( "://" )
		if dbTypeEndPos <= 0:
			raise ConfigurationException(
				"Unable to get database type from URI '%s'." % dbURI )

		dbType = dbURI[ dbTypeStartPos : dbTypeEndPos ]

		if (dbType in SUPPORTED_DBS):
			return dbType
		else:
			raise ConfigurationException(
				"Unknown database type '%s' in URI '%s'." % dbType, dbURI )
	# _getDBType


	@staticmethod
	def _renameSQLiteCols( cursor, cls, cols ):
		"""
		SQLite does not have an ALTER TABLE CHANGE function.  Since columns can
		not be renamed, instead we need to migrate the table schema. The method
		to do this is:
		- Backup the old table
		- Create the updated table
		- Copy data across
		- Delete the old table
		"""

		tableName = cls.sqlmeta.table

		# Determine if the update is required and upon which fields
		# it is required.
		colsToRename = []
		for columnName, newName in cls.RENAME_COLS:
			if columnName in cols:
				log.info( "Renaming column from %s to %s",
						columnName, newName )

				if newName not in cols:
					colsToRename.append( (columnName, newName) )
				else:
					log.critical( "Column %s already exists, can't rename",
							newName )


		if colsToRename:

			# Get the original schema
			sql = "select sql from sqlite_master " \
					"where type= 'table' " \
					"and name = '%s'" % tableName
			cursor.execute( sql )
			result = cursor.fetchall()
			tableSchema = None
			try:
				tableSchema = result[0][0]
			except Exception, ex:
				log.critical( "Unable to get table definition for %s while "
						"renaming columns.", tableName )
				raise ex


			# Build the replacement schema
			for (columnName, newName) in colsToRename:
				regex = re.compile('([(,]\s+)%s(\s)' % columnName,
						re.MULTILINE)
				tableSchema = regex.sub( r'\1%s\2' % newName, tableSchema )


			# Backup the original table
			import datetime
			timestampStr = datetime.datetime.now().strftime( "%Y%m%d%H%M%S" )
			tmpTableName = "tmp_%s_%s" % (tableName, timestampStr)
			sql = "ALTER TABLE %s RENAME TO %s" % (tableName, tmpTableName)
			cursor.execute( sql )


			# Create the updated table using the new schema
			cursor.execute( tableSchema )


			# Build the string of old column names
			oldCols = ','.join( [col for col, colType in cols.items()] )


			# Build the string of new column names
			newColList = []
			for col, colType in cols.items():
				renamed = False
				for oldName, newName in colsToRename:
					if col == oldName:
						newColList.append( newName )
						renamed = True
				if not renamed:
					newColList.append( col )
			newCols = ','.join( newColList )


			# Migrate data across
			sql = "INSERT INTO %s( %s ) SELECT %s FROM %s" % \
				(tableName, newCols, oldCols, tmpTableName)
			cursor.execute( sql )


			# Delete the backup of the original table
			sql = "DROP TABLE %s" % tmpTableName
			cursor.execute( sql )

		# end if colsToRename
	# _renameSQLiteCols


	@staticmethod
	def _renameMySQLCols( cursor, cls, cols ):
		tableName = cls.sqlmeta.table

		for columnName, newName in cls.RENAME_COLS:
			if columnName in cols:
				log.info( "Renaming column from %s to %s",
					columnName, newName )

				if newName not in cols:
					sql = "ALTER TABLE %s CHANGE %s %s %s" % \
						(tableName, columnName, newName,
						cols[ columnName ])
					cursor.execute( sql )
				else:
					log.critical(
						"Column %s already exists, can't rename",
						newName )
	# _renameMySQLCols


	# This is circumventing the TurboGears and SQLObject database connections
	# here. This can be removed once `tg-admin sql update` works.
	@staticmethod
	def verifySchemas():
		""" Iterates through database tables and classes, applying any necessary
		checks or schematic updates that may be defined within those DAO classes.

		Schema checks/changes are communicated through the following class-scoped
		(list of 2-tuple) properties:

			VERIFY_COLS				Adds column(s) if missing.
									eg: [("my_column", "varchar(16)")]


			RENAME_COLS				Renames column(s).
									eg: [("old_column", "new_column")]

			FORCE_MIGRATE_SCHEMA		Mercilessly drops and recreates table if any
									column definition differs from the DB.
									NOTE: data in the table is LOST as a result.
									Overrides other *_COLS options.
									eg: [("my_column", "varchar(32)")]

		"""

		dbURI = turbogears.config.get( "sqlobject.dburi" )
		db = None
		cursor = None
		columnAquirerFunc = None
		dbType = DictSQLObject._getDBType( dbURI )

		if dbType == DB_TYPE_SQLITE:

			for cls in DictSQLObjectType.s_classes:
				cls.createTable( True )

			m = re.search( "sqlite://(/.+$)", dbURI )
			try:
				filename, = m.groups()

			except (AttributeError, ValueError):
				log.error( "Could not parse SQLite database URI.")
				return False

			# remove any optional debug arguments ("?xxx=yyy")
			filename = filename.rsplit( "?", 1 )[0]

			db = sqlite.connect( filename )
			cursor = db.cursor()

			columnAquirerFunc = getSQLiteTableColumnDict

		elif dbType == DB_TYPE_MYSQL:

			m = re.search( "//([\w\.\-]+):(.+)@([\w\.\-]+):(\d+)/([\w\$]+)", dbURI )
			try:
				user, password, host, port, dbname = m.groups()

			except (AttributeError, ValueError):
				log.error( "Could not parse MySQL database URI.")
				log.error( "Not verifying that database is in sync with model defs." )
				return False

			# Set up connection to the database
			db = MySQLdb.connect( host = host, port = int( port ), db = dbname,
								  user = user, passwd = password )
			cursor = db.cursor()

			columnAquirerFunc = getMySQLTableColumnDict

		else:
			# Failsafe to ensure that we handle all the types allowed through by
			# _getDBType.
			raise ValueError(
				"Unknown database type '%s'. Unable to connect to database."
				% dbType )


		# map of tableName -> table class; accumulates FORCE_MIGRATE_SCHEMA changes
		schemaChanges = {}

		# Iterate over DAO classes, applying schema changes as needed
		for cls in DictSQLObjectType.s_classes:
			cls.createTable( True )
			tableName = cls.sqlmeta.table

			# get list of actual columns in table (ie: fetch from DB)
			cols = columnAquirerFunc( cursor, tableName )

			if hasattr( cls, "FORCE_MIGRATE_SCHEMA" ):
				# Get a list of cols already defined in that table

				for colName, colDefinition in cls.FORCE_MIGRATE_SCHEMA:
					if colName in cols and cols[colName].lower() != colDefinition:
						schemaChanges[tableName] = cls
						continue

			if hasattr( cls, "VERIFY_COLS" ):

				for colName, colDefinition in cls.VERIFY_COLS:

					if colName not in cols:
						cursor.execute( "alter table %s add %s %s;" %
										(tableName, colName, colDefinition) )
						cursor.fetchall()
						log.info( "Added missing column %s to %s" %
								  (colName, tableName) )

					if colName in cols and cols[colName].lower() != colDefinition:
						log.critical( "Existing field with wrong type: "
									  "%s is %s, should be %s" %
									  (colName, cols[colName], colDefinition) )

			if hasattr( cls, "RENAME_COLS" ):

				if dbType == DB_TYPE_SQLITE:
					DictSQLObject._renameSQLiteCols( cursor, cls, cols )

				elif dbType == DB_TYPE_MYSQL:
					DictSQLObject._renameMySQLCols( cursor, cls, cols )

				else:
					# Failsafe to ensure that we handle all the types allowed
					# through by _getDBType.
					raise ValueError(
						"Unknown database type '%s'. Unable to rename columns."
						% dbType )

		db.commit()

		if schemaChanges:
			for tableName, cls in schemaChanges.items():

				log.warning(
					"destructively migrating table '%s' to new schema", tableName )

				try:
					cls.dropTable( ifExists = True, dropJoinTables = True )
					cls.createTable( True )
				except:
					log.exception( "Couldn't recreate table '%s'", tableName )
					raise

			# end for
		# end if

		db.close()


# identity models.
class Visit( DictSQLObject ):
	class sqlmeta:
		table = "visit"

	visit_key = StringCol(length=40, alternateID=True,
						alternateMethodName="by_visit_key")
	created = DateTimeCol(default=datetime.now)
	expiry = DateTimeCol()

	# new column, make sure the schema is updated accordingly
	auth_method = StringCol( length = 32, default = LdapUtil.getAuthMethod )

	VERIFY_COLS = [ ("auth_method", "varchar(32)") ]

	def lookup_visit(cls, visit_key):
		try:
			return cls.by_visit_key(visit_key)
		except SQLObjectNotFound:
			return None
	lookup_visit = classmethod(lookup_visit)

# end class Visit


class VisitIdentity( DictSQLObject ):
	visit_key = StringCol( length=40, alternateID=True,
						  alternateMethodName="by_visit_key" )
	user_id = IntCol()

# end class VisitIdentity


class Group( DictSQLObject ):
	"""
	An ultra-simple group definition.
	"""

	# names like "Group", "Order" and "User" are reserved words in SQL
	# so we set the name to something safe for SQL
	class sqlmeta:
		table="tg_group"

	group_name = UnicodeCol( length=128, alternateID=True,
							 alternateMethodName="by_group_name" )
	display_name = UnicodeCol( length=255 )
	created = DateTimeCol( default=datetime.now )

	# collection of all users belonging to this group
	users = RelatedJoin( "User", intermediateTable="user_group",
						 joinColumn="group_id", otherColumn="user_id" )

	# collection of all permissions for this group
	permissions = RelatedJoin( "Permission", joinColumn="group_id",
							   intermediateTable="group_permission",
							   otherColumn="permission_id" )

	# recreate table (dropping data) if column def differs from below.
	# access control groups will be reinserted after recreation.
	FORCE_MIGRATE_SCHEMA = [ ("group_name", "varchar(128)") ]

# end class Group


class User( DictSQLObject ):
	"""
	Reasonably basic User definition. Probably would want additional attributes.
	"""
	# names like "Group", "Order" and "User" are reserved words in SQL
	# so we set the name to something safe for SQL
	class sqlmeta:
		table="tg_user"

	# This retains the underscore because identity and catwalk both use user_name
	user_name = UnicodeCol( length=32, alternateID=True,
						   alternateMethodName="by_user_name" )
	password = UnicodeCol( length=32 )
	serveruser = UnicodeCol( length=32, default="demo" )

	# groups this user belongs to
	groups = RelatedJoin( "Group", intermediateTable="user_group",
						  joinColumn="user_id", otherColumn="group_id" )

	def isAdmin( self ):
		for group in self.groups:
			if group.group_name == "admin":
				return True

		return False
	# isAdmin


	def isDefaultAdmin( self ):
		return self.user_name == "admin"


	@classmethod
	def byName( self, username ):
		try:
			return self.by_user_name( username )
		except SQLObjectNotFound, ex:
			log.debug( "No user named '%s'", username )
			return None
	# byName


	def hasPermissions( self, *permissions ):
		assert self.groups
		groups = [g.group_name for g in self.groups]
		return auth.Permission( *permissions ).canAccess( groups )
	# hasPermissions


	def hasOwnerPermissions( self, *permissions ):
		ownerPerms = self.getOwnerPermissions()
		for p in permissions:
			if p not in ownerPerms:
				return False

		return True
	# hasOwnerPermissions


	def hasOtherPermissions( self, *permissions ):
		otherPerms = self.getOtherPermissions()
		for p in permissions:
			if p not in otherPerms:
				return False

		return True
	# hasOtherPermissions


	def getOwnerPermissions( self ):
		assert self.groups
		groups = [g.group_name for g in self.groups]
		return auth.Permission.getRights( groups, True )
	# getOwnerPermissions


	def getOtherPermissions( self ):
		assert self.groups
		groups = [g.group_name for g in self.groups]
		return auth.Permission.getRights( groups, False )
	# getOtherPermissions


	def _get_permissions( self ):
		perms = set()
		for g in self.groups:
			perms = perms | set(g.permissions)
		return perms

	def _set_password( self, cleartext_password ):
		"Runs cleartext_password through the hash algorithm before saving."
		hash = identity.encrypt_password(cleartext_password)
		self._SO_set_password(hash)

	def set_password_raw( self, password ):
		"Saves the password as-is to the database."
		self._SO_set_password(password)


class Permission( DictSQLObject ):
	permission_name = UnicodeCol( length=16, alternateID=True,
								 alternateMethodName="by_permission_name" )
	description = UnicodeCol( length=255 )

	groups = RelatedJoin( "Group",
						intermediateTable="group_permission",
						 joinColumn="permission_id",
						 otherColumn="group_id" )


log.info( "Initialising model" )
Visit.createTable( True )
VisitIdentity.createTable( True )
Group.createTable( True )
User.createTable( True )
Permission.createTable( True )


# Initialise users and groups which should always exist
def createGroup( name, displayName = None ):
	results = list( Group.select( Group.q.group_name == name ) )
	if not results:
		log.info( "creating group '%s'", name )
		grouprec = Group( group_name = name,
						  display_name = displayName or name )
	else:
		log.debug( "group '%s' exists", name )
		grouprec = results[0]


def setupAdminUser( name, password, serveruser ):
	# Retrieve admin group
	results = list( Group.select( Group.q.group_name == "admin" ) )
	adminGroup = results[0]

	# print "Setting up admin user: %s" % (name )
	# Make sure admin account is set up
	results = list( User.select( User.q.user_name == name ) )
	if not results:
		userrec = User(
			user_name = name,
			password = password,
			serveruser = serveruser )
	else:
		userrec = results[0]

	if userrec not in adminGroup.users:
		adminGroup.addUser( userrec )


def checkUserGroups():
	"""
	Checks that all users have at least 1 group assigned, and if not,
	assigns them to the default group, given by configuration key
	`web_console.authorisation.default_group`.
	"""

	defaultGroup = turbogears.config.get(
		'web_console.authorisation.default_group', None )

	if not defaultGroup:
		log.warning( "No default group defined, user groups will not be checked" )
		return

	log.info( "Checking user groups" )
	group = Group.by_group_name( defaultGroup )

	if not group:
		raise Exception(
			"Non-existant group name '%s', groups are: %s" \
			% (defaultGroup, [g.group_name for g in Group.select()]) )

	for user in User.select():
		if not user.groups:
			log.info( "User '%s' ungrouped, adding to group '%s'",
				user.user_name, group.group_name )
			group.addUser( user )

# checkUserGroups


# invalidate user sessions when authentication method has been changed, by
# deleting visit records with authentication method different from current
def clearUserSessions():
	authMethod = LdapUtil.getAuthMethod()

	for item in Visit.select(
			"auth_method is null or auth_method != '%s'" % authMethod ):
		item.destroySelf()

# clearUserSessions


def init():
	createGroup( "admin" )
	setupAdminUser( "admin", "admin", "" )

	if not turbogears.config.get( 'web_console.authorisation.on', False ):
		log.info( "Authorisation not enabled" )
		return

	if not auth.Permission.GroupRights:
		raise Exception( "Permissions not loaded" )

	for group_name in auth.Permission.GroupRights:
		createGroup( group_name )

	checkUserGroups()

	clearUserSessions()

	hub.commit()
# initModel

# model.py

