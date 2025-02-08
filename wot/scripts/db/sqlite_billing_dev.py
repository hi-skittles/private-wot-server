import functools
import hashlib
import socket
import sqlite3
import struct
import os

import BackgroundTask
import BigWorld
import ResMgr

DIR_NAME = "server/"
FILENAME = "dev_test_1.sqlite"
SHORT_FILENAME = "server/dev_test_1.sqlite"

NUM_THREADS = 4

from billing_system_settings import SHOULD_ACCEPT_UNKNOWN_USERS
from billing_system_settings import SHOULD_REMEMBER_UNKNOWN_USERS
from billing_system_settings import ENTITY_TYPE_FOR_UNKNOWN_USERS


def hashPassword( password ):
	return hashlib.md5( password ).hexdigest()

class GetTask( BackgroundTask.BackgroundTask ):
	def __init__( self, username, password, response ):
		self.username = username
		self.password = password
		self.response = response
	
	def doBackgroundTask( self, bgTaskMgr, connection ):
		c = connection.cursor()
		results = c.execute( """SELECT password, entity_type, entity_id
					FROM accounts WHERE username=?""",
		                     (self.username,) )
		self.result = results.fetchone()
		bgTaskMgr.addMainThreadTask( self )
	
	def doMainThreadTask( self, bgTaskMgr ):
		try:
			self.processResult( self.result )
		except:
			self.response.failureDBError()
			raise
	
	def processResult( self, result ):
		if result:
			if hashPassword( self.password ) == result[0]:
				entityType, entityID = result[1], result[2]
				if entityID is None:
					if entityType is None:
						entityType = ENTITY_TYPE_FOR_UNKNOWN_USERS
					self.response.createNewEntity( entityType, True )
				else:
					self.response.loadEntity( entityType, entityID )
			else:
				self.response.failureInvalidPassword()
		
		elif SHOULD_ACCEPT_UNKNOWN_USERS:
			self.response.createNewEntity( ENTITY_TYPE_FOR_UNKNOWN_USERS,
			                               SHOULD_REMEMBER_UNKNOWN_USERS )
		else:
			self.response.failureNoSuchUser()


class SetTask( BackgroundTask.BackgroundTask ):
	def __init__( self, username, password, entityType, entityID ):
		self.username = username
		self.password = password
		self.entityType = entityType
		self.entityID = entityID
	
	def doBackgroundTask( self, bgTaskMgr, connection ):
		c = connection.cursor()
		
		# Just for debugging. REPLACE will cause deletion
		c.execute( "DELETE FROM accounts WHERE entity_type=? and entity_id=?",
		           (self.entityType, self.entityID) )
		
		if c.rowcount != 0:
			print "BillingSystem.setEntityKeyForAccount: " \
			      "An account already existed with this entity key"
		
		c.execute( "REPLACE INTO accounts VALUES (?,?,?,?)",
		           (self.username, hashPassword( self.password ),
		            self.entityType, self.entityID) )
		connection.commit()



# This class is an example integration with a billing system. It stores the
# account information in an SQLite database.
class BillingSystem( object ):
	def __init__( self ):
		filename = os.path.join( ResMgr.resolveToAbsolutePath( DIR_NAME ),
		                         FILENAME )
		print "BillingSystem.__init__: Account database is", filename
		
		connection = sqlite3.connect( filename )
		c = connection.cursor()
		
		try:
			c.execute( "SELECT * FROM accounts" )
		except sqlite3.OperationalError:
			print "Creating accounts table"
			c.execute( """CREATE TABLE accounts
					(username TEXT PRIMARY KEY,
					 password TEXT,
					 entity_type TEXT,
					 entity_id INTEGER,
					 UNIQUE (entity_type, entity_ID) )""" )
		connection.commit()
		
		self.bgTaskMgr = BackgroundTask.Manager()
		connectionCreator = functools.partial( sqlite3.connect, filename )
		self.bgTaskMgr.startThreads( NUM_THREADS, connectionCreator )
	
	
	# This method validates account details and returns the entity key that this
	# account should use.
	def getEntityKeyForAccount( self, username, password,
	                            clientAddr, response ):
		ip = socket.inet_ntoa(
			struct.pack( '!I', socket.ntohl( clientAddr[0] ) ) )
		port = socket.ntohs( clientAddr[1] )
		
		print "%s is logging in from %s:%d" % (username, ip, port)
		self.bgTaskMgr.addBackgroundTask(
			GetTask( username, password, response ) )
	
	# This method is called to add new account details. This will only be called
	# if createNewEntity is called with shouldRemember as True.
	def setEntityKeyForAccount( self, username, password,
	                            entityType, entityID ):
		self.bgTaskMgr.addBackgroundTask(
			SetTask( username, password, entityType, entityID ) )

# sqlite_billing_dev.py
