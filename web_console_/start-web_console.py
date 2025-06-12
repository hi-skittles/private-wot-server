#!/usr/bin/env python

# Begin loading our distributed eggs.
#
# Here we're using an undocumented feature of pkg_resources which allows the us
# to "require" eggs without conflicting with eggs already installed in
# sys.path. This is done by adding a __requires__ list containing egg
# directives to the __main__ module. It's currently preferable to using
# pkg_resources.require() to use eggs.

# See ../pycommon/redist/readme.txt for more details.
#
# More information at:
# http://mail.python.org/pipermail/distutils-sig/2005-September/005164.html

__requires__ = [ "PyAMF==0.3.1", "CherryPy==2.3.0", "TurboJson>=1.2.1", "TurboGears<2.0.0" ]

# Add the path containing packages to sys.path
import bwsetup
bwsetup.addPath( ".." )
bwsetup.addPath( "../pycommon/redist", 0 )

# Hook into the profiling threads as early as possible.
# NOTE: Must come before import logging and import turbogears
from pycommon import bw_profile

# The act of importing the pkg_resources module will cause it to automatically
# veryify the existence of each package in our __requires__ list, and add it to
# sys.path.
import pkg_resources

import sys
import os
import optparse
import logging

log = logging.getLogger( __name__ )

HAS_MY_SQL = True
STAT_GRAPHER_LOGGING = False

try:
	import MySQLdb
except ImportError:
	HAS_MY_SQL = False


def main( configFile, syncDb = False ):
	import turbogears
	import cherrypy
	cherrypy.lowercase_api = True

	from web_console.common import util
	logging.getLogger().setLevel( logging.INFO )

	turbogears.update_config( configfile = configFile,
		modulename = "root.config" )

	import os
	try:
		user_config_file = os.getenv("HOME") + '/.bw_web_console.cfg'
		turbogears.update_config( user_config_file )
		print "configuration updated from %s" % user_config_file
	except TypeError, t:
		# thrown if HOME not set
		pass
	except KeyError, k:
		# thrown when:
		#  - file doesn't exist, or
		#  - file exists but doesn't contain a 'global' section
		pass


	if HAS_MY_SQL:
		try:
			import root.controllers
		except MySQLdb.OperationalError, e:
			log.error( "Couldn't connect to the MySQL database:\n%s", str( e ) )

			sys.exit( 1 )
	else:
		import root.controllers
		
	from web_console.common.authorisation import Permission
	Permission.initRights()

	try:
		rootController = root.controllers.Root()
	except ImportError, e:
		log.error( "%s\nA shared library may be restricted by SELinux. "
			"Either disable SELinux or relax the security context of the "
			"library by:\n'$ semanage fcontext -a -t SHARED_LIB'\n'"
			"$ chcon -f -t textrel_shlib_t SHARED_LIB'", str( e ) )
		sys.exit( 1 )

	# Make sure database schemas are up-to-date
	import web_console.common.model
	web_console.common.model.DictSQLObject.verifySchemas()
	
	# Exit now that database has been synced
	if syncDb:
		log.info( "Database synced, exiting" )
		sys.exit( 0 )

	setupLoggers()
	
	from turbogears import config
	from web_console.common.ldap_util import LdapUtil

	# check and validate LDAP configuration
	if LdapUtil.isAuthByLdapEnabled():
		log.info( "Authentication by LDAP is enabled" )
		
		# validate the file permission
		if  config.get( "server.environment" ) == "production" \
				and util.isFileReadableByOthers( configFile ):
			log.error( 'The file permission of config file %s is incorrect. ' \
				'It MUST NOT be readable by other users when authentication ' \
				'by LDAP is enabled(identity.auth_method = "ldap"). Please ' \
				'correct the file permission and try again.', configFile )
			sys.exit( 1 )

		# validate the LDAP configuration
		if not LdapUtil().validateLdapConfig():
			log.error( "Failed to validate the LDAP configurations. Please "
					"correct the configurations and try again." )
			sys.exit( 1 )


	# WebConsole Self Profiling configuration
	if bw_profile.isAvailable():
		dumpDir = config.get( 'web_console.bw_profile.dump_dir', '' )

		if not dumpDir:
			errMessage = "Self profiling is enabled but no JSON dump directory " \
				"has been configured. Please set " \
				"'web_console.bw_profile.dump_dir' in your config file."
			log.error( errMessage )
			raise RuntimeError, errMessage

		absDumpDir = os.path.abspath( dumpDir )
		bw_profile.setJsonDumpDir( absDumpDir )

	# schedule regular tasks
	from web_console.common import jobs
	turbogears.startup.call_on_startup.append( jobs.scheduleTasks )

	cherrypy.server.on_start_server_list.append( rootController.onStartServer )
	turbogears.start_server( rootController )



def setupLoggers():

	# Setup stat_grapher logs:
	# Don't propgate stat_grapher logs up to the root logger (which typically
	# dumps to stdout)
	logging.getLogger( "stat_grapher" ).propagate = False

	if STAT_GRAPHER_LOGGING:
		logFormatter = logging.Formatter( "%(name)s %(asctime)s: %(message)s" )
		logFormatterNewline = \
			logging.Formatter( "\n%(name)s %(asctime)s: %(message)s" )

		sqlLog = logging.getLogger( "stat_grapher.sql" )
		sqlLogHandler = logging.FileHandler(
			"stat_grapher/stat_grapher_sql.log", "w")
		sqlLogHandler.setFormatter( logFormatterNewline )
		sqlLog.addHandler( sqlLogHandler )

		apiLog = logging.getLogger( "stat_grapher.api" )
		apiLogHandler = logging.FileHandler(
			"stat_grapher/stat_grapher_api.log", "w")
		apiLogHandler.setFormatter( logFormatter )
		apiLog.addHandler( apiLogHandler )

		amfLog = logging.getLogger( "stat_grapher.amf" )
		amfLogHandler = logging.FileHandler(
			"stat_grapher/stat_grapher_amf.log", "w")
		amfLogHandler.setFormatter( logFormatter )
		amfLog.addHandler( amfLogHandler )

		mdLog = logging.getLogger( "stat_grapher.md" )
		mdLogHandler = logging.FileHandler(
			"stat_grapher/stat_grapher_md.log", "w")
		mdLogHandler.setFormatter( logFormatter )
		mdLog.addHandler( mdLogHandler )

# setupLoggers


def parseArgs():
	parser = optparse.OptionParser( usage="start-web_console.py [options] "
									"[CONFIG_FILE; default=dev.cfg]" )

	parser.add_option( "-s", "--syncdb",
		action = "store_true", dest = "syncdb",
		default = False,
		help = "Sync WebConsole database and exit" )

	parser.add_option( "-d", "--daemon",
		action = "store_false", dest = "foreground",
		default = True,
		help = "run as daemon (default in foreground)" )

	parser.add_option( "-o", "--output",
		type = "string", dest = "output",
		help = "daemon output log file (default '%default')" )

	parser.add_option( "-e", "--error-output",
		type = "string", dest = "error_output",
		help = "daemon error log file (default '%default')" )

	parser.add_option( "-p", "--pid-file",
		type = "string", dest = "pid_file",
		default = "web_console.pid",
		help = "daemon PID file (default '%default')" )

	parser.add_option( "-c", "--chdir",
		type = "string", dest = "chdir",
		help = "daemon working directory" )

	deprecated = optparse.OptionGroup( parser, "Deprecated Options",
		"These options have been deprecated and may be removed "
		"in the future." )

	deprecated.add_option( "", "--home",
		type = "string", dest = "home",
		help = "daemon working directory (superseded by --chdir)" )

	parser.add_option_group( deprecated )


	options, args = parser.parse_args()

	return options, args

# parseArgs


if __name__ == "__main__":

	configFile = 'dev.cfg'

	options, args = parseArgs()
	if len( args ) > 0:
		configFile = args[0]

	try:
		import turbogears
	except ImportError, e:
		print "ERROR: Unable to import TurboGears module (%s)" % str(e)
		sys.exit( 1 )
	
	if options.syncdb and not options.foreground:
		
		print "Error: --syncdb is incompatible with the --daemon option."
		sys.exit( 1 )
		
	elif options.foreground:

		# Redirect stdout/stderr if necessary
		if options.output:
			try:
				fd = os.open( options.output, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0644 )
				os.dup2( fd, 1 )
				os.close( fd )
			except Exception, e:
				print "Error while attempting to redirect stdout to file '%s'" % options.output
				print str(e)

		if options.error_output:
			try:
				fd = os.open( options.error_output, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0644 )
				os.dup2( fd, 2 )
				os.close( fd )
			except Exception, e:
				print "Error while attempting to redirect stderr to file '%s'" % options.error_output
				print str(e)

		main( configFile, options.syncdb )
	else:

		if not options.output:
			options.output = "/dev/null"
		if not options.error_output:
			options.error_output = "/dev/null"

		chdirPath = ""

		if options.home:
			log.warn( "'--home' has been deprecated and may be removed "
				"in the future.\nUse '--chdir' instead." )

		if options.chdir:
			if options.home:
				log.warn( "defaulting to chdir rather than home" )

			chdirPath = options.chdir

		elif options.home:
			chdirPath = options.home

		if not chdirPath:
			defaultDir = os.path.abspath( os.path.dirname( sys.argv[0] ) )
			log.warn( "defaulting daemon cwd to stat_logger directory: '%s'",
				defaultDir )
			chdirPath = defaultDir


		from pycommon.daemon import Daemon
		d = Daemon( run = main,
			args = (configFile,),
			workingDir = chdirPath,
			outFile = options.output,
			errFile = options.error_output,
			pidFile = options.pid_file,
			umask = 0033
		)
		d.start()
