import functools, hashlib, socket, struct, mysql.connector

import BigWorld, BackgroundTask, ResMgr
from bwdebug import DEBUG_MSG, INFO_MSG, WARNING_MSG
from billing_system_settings import SHOULD_ACCEPT_UNKNOWN_USERS
from billing_system_settings import SHOULD_REMEMBER_UNKNOWN_USERS
from billing_system_settings import ENTITY_TYPE_FOR_UNKNOWN_USERS

NUM_THREADS = 4
IS_DEV = True
ELOGS = True


class DB_CONSTS:
	DATABASE_NAME = "player_data_dev1"
	PTABLE_NAME = "accounts0"
	DTABLE_NAME = "accounts1"
	TABLE_NAME = DTABLE_NAME if IS_DEV else PTABLE_NAME


def hashPassword(password):
	return hashlib.md5(password).hexdigest()


class GetTask(BackgroundTask.BackgroundTask):
	def __init__(self, logOnName, password, response):
		self.logOnName = logOnName
		self.password = password
		self.response = response
		self.result = None
	
	def doBackgroundTask(self, bgTaskMgr, connection):
		c = connection.cursor()
		if ELOGS: DEBUG_MSG('BillingSystem :: Checking for %s' % self.logOnName)
		c.execute("""SELECT * FROM {} WHERE logOnName=%s""".format(DB_CONSTS.TABLE_NAME),
		          (self.logOnName,))
		self.result = c.fetchone()
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		try:
			self.processResult(self.result)
		except:
			self.response.failureDBError()
			raise
	
	def processResult(self, result):
		if result:
			if hashPassword(self.password) == result[1]:
				if ELOGS: DEBUG_MSG('BillingSystem :: User %s logged in' % self.logOnName)
				if True:   # len([e for e in BigWorld.entities.values() if e.className == 'Account'])
					self.response.loadEntityByName('Account', self.logOnName, False)
				else:
					self.response.loadEntityByName('Login', self.logOnName, False)
			else:
				self.response.failureInvalidPassword()
		elif SHOULD_ACCEPT_UNKNOWN_USERS:
			if ELOGS: DEBUG_MSG(
				'[INFO] BillingSystem :: No result found for %s. Creating new entity since unknown users are enabled.' % self.logOnName)
			self.response.createNewEntity(ENTITY_TYPE_FOR_UNKNOWN_USERS, SHOULD_REMEMBER_UNKNOWN_USERS)
		else:
			if ELOGS: DEBUG_MSG('BillingSystem :: No result found for %s' % self.logOnName)
			self.response.failureNoSuchUser()


class SetTask(BackgroundTask.BackgroundTask):
	def __init__(self, logOnName, password):
		self.logOnName = logOnName
		self.password = password
	
	# self.username = self.logOnName.split('@')[0] + str(random.randint(1000, 9999))
	
	def doBackgroundTask(self, bgTaskMgr, connection):
		c = connection.cursor(buffered=True)
		
		# Just for debugging. REPLACE will cause deletion
		c.execute("""DELETE FROM {} WHERE logOnName=%s""".format(DB_CONSTS.TABLE_NAME), (self.logOnName,))
		
		if c.rowcount != 0:
			if ELOGS: DEBUG_MSG(
				"BillingSystem.setEntityKeyForAccount:\nAn account already existed with this entity key")
		
		c.execute("""REPLACE INTO {} VALUES (%s, %s)""".format(DB_CONSTS.TABLE_NAME),
		          (self.logOnName, hashPassword(self.password)))
		connection.commit()


# This class is an example integration with a billing system. It stores the
# account information in an SQLite database.
class BillingSystem(object):
	def __init__(self):
		self.connection = mysql.connector.connect(
			host='localhost',
			user='bigworld',
			password='bigworld',
			database=DB_CONSTS.DATABASE_NAME
		)
		
		INFO_MSG('BillingSystem :: Account database is {}.{}'.format(DB_CONSTS.DATABASE_NAME, DB_CONSTS.TABLE_NAME))
		c = self.connection.cursor(buffered=True)
		if self.connection.is_connected(): INFO_MSG("BillingSystem :: Connected to %s" % self.connection.server_host)
		
		try:
			c.execute("SELECT * FROM {}".format(DB_CONSTS.TABLE_NAME))
		except mysql.connector.errors.Error:
			WARNING_MSG("BillingSystem :: Table %s does not exist. Creating." % DB_CONSTS.TABLE_NAME)
			c.execute("""create table {}
			(
				logOnName  varchar(128) not null primary key unique,
				password   varchar(255) not null
			)""".format(DB_CONSTS.TABLE_NAME))
		self.connection.commit()
		
		self.bgTaskMgr = BackgroundTask.Manager('BillingSystem')
		connectionCreator = functools.partial(mysql.connector.connect,
		                                      host='localhost',
		                                      user='bigworld',
		                                      password='bigworld',
		                                      database=DB_CONSTS.DATABASE_NAME)
		self.bgTaskMgr.startThreads(NUM_THREADS, connectionCreator)
	
	# This method validates account details and returns the entity key that this
	# account should use.
	def getEntityKeyForAccount(self, logOnName, password, clientAddr, response):
		ip = socket.inet_ntoa(struct.pack('!I', socket.ntohl(clientAddr[0])))
		port = socket.ntohs(clientAddr[1])
		if ELOGS: DEBUG_MSG(
			'BillingSystem :: {} logging in from {}:{} ({}) with password "{}".'.format(logOnName, ip, port, clientAddr,
			                                                                            password))
		
		self.bgTaskMgr.addBackgroundTask(GetTask(logOnName, password, response))
	
	# This method is called to add new account details. This will only be called
	# if createNewEntity is called with shouldRemember as True.
	def setEntityKeyForAccount(self, logOnName, password, entityType, entityID):
		self.bgTaskMgr.addBackgroundTask(SetTask(logOnName, password))
