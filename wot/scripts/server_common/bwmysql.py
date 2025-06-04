"""
Low-level wrapper module for interacting with the BigWorld MySQL server
"""

import os
import subprocess
import oursql
import re

from bwtest import config
from bwtest import log


def executeSQL(query, host=config.CLUSTER_DB_HOST,
               user=config.CLUSTER_DB_USERNAME,
               passwd=config.CLUSTER_DB_PASSWORD,
               db=config.CLUSTER_DB_DATABASENAME,
               useDB=True):
	"""
	This method executes a command on the database and returns the results.
	@param query: SQL query to execute
	@param host:  Provide this to use a different host to the one
	configured in bw_<username>.xml
	@param user: Provide this to use a different username to the one
	configured in bw_<username>.xml
	@param passwd: Provide this to use a different password to the one
	configured in bw_<username>.xml
	@param db: Provide this to use a different database name to the one
	configured in bw_<username>.xml
	@param useDB: Set this False to not connect to the BigWorld database
	"""
	
	log.info("executeSQL: executing '%s' for %s@%s, pass=%s, db='%s'" %
	         (query, user, host, passwd, db))
	
	if useDB:
		conn = oursql.connect(host, user, passwd, db=db)
	else:
		conn = oursql.connect(host, user, passwd)
	
	cursor = conn.cursor()
	
	# Find special delimiters
	delimiters = re.compile('DELIMITER *(\S*)', re.I)
	result = delimiters.split(query)
	
	# Insert default delimiter and separate delimiters and sql
	result.insert(0, ';')
	delimiter = result[0::2]
	section = result[1::2]
	
	# Split queries on delimiters and execute
	for i in range(len(delimiter)):
		queries = section[i].split(delimiter[i])
		queries = [q.strip() for q in queries if q.strip()]
		for query in queries:
			try:
				cursor.execute(query, plain_query=True)
				results = cursor.fetchall()
			except:
				return []
			finally:
				cursor.close()
				conn.commit()
				conn.close()
	
	return results


def stopMysqlServer(machine, local=False):
	"""
	This method stops the mysql server on given machine. 
	Requires passwordless login to the mysql machine.
	@param machine: Hostname of machine running MySQL
	@param local: Use sudo instead of SSH if this is set to True
	"""
	
	log.info("Stopping MySQL server on machine %s" % machine)
	if local:
		prog = subprocess.Popen("sudo /etc/init.d/mysqld stop",
		                        stderr=subprocess.PIPE, shell=True)
	else:
		prog = subprocess.Popen(["ssh", 'root@' + machine,
		                         '/etc/init.d/mysqld stop'],
		                        stderr=subprocess.PIPE)
	errdata = prog.communicate()[1]
	if errdata:
		log.error("stopMysqlServer(): '%s'" % errdata)
		return False
	
	return True


def startMysqlServer(machine, local=False):
	"""
	This method starts the mysql server on given machine. 
	Requires passwordless login to the mysql machine.
	@param machine: Hostname of machine running MySQL
	@param local: Use sudo instead of SSH if this is set to True
	"""
	
	log.info("Starting MySQL server on machine %s" % machine)
	if local:
		prog = subprocess.Popen("sudo /etc/init.d/mysqld start",
		                        stderr=subprocess.PIPE, shell=True)
	else:
		prog = subprocess.Popen(["ssh", 'root@' + machine,
		                         '/etc/init.d/mysqld start'],
		                        stderr=subprocess.PIPE)
	errdata = prog.communicate()[1]
	if errdata:
		log.error("startMysqlServer(): '%s'" % errdata)
		return False
	
	return True
