"""
Configuration. The attributes here will be populated from 
user_config/user_config.xml and user_config/server/bw_<username>.xml
"""
import sys, os
try:
	from pwd import getpwnam
except ImportError:
	pass #On Windows, pwd doesn't exist
import getpass
from xml.dom.minidom import parse

#default test root
TEST_ROOT = os.path.dirname( os.path.realpath( __file__ ) )+"/.."

# List all supported tags here
SUPPORTED_TAGS = [ "WIP", "STAGED", "MANUAL" ]

# Workflow tags:
# WIP - test case is a work-in-progress. A failure may be expected.
# STAGED - test case is complete but awaits verification on a staging server

# Test type tags:
# MANUAL - test case has a manual input entry which make it non-automatic  

# Arbitrary tags can be used. Supported tags just specify tags 
# that have meaning in terms of the framework 

#None setting dynamically populated settings
DRY_RUN = None

_appdir = os.path.dirname( os.path.abspath( __file__ ) )

"""
if not os.path.exists( _appdir + "/../../../game" ):
	BIGWORLD_FOLDER="bigworld"
	BIGWORLD_SOURCE_FOLDER=""
	CLUSTER_BW_ROOT = TEST_ROOT + "/.."
else:
	BIGWORLD_FOLDER="game/bigworld"
	BIGWORLD_SOURCE_FOLDER="game"
	CLUSTER_BW_ROOT = TEST_ROOT + "/../.."
	if os.path.exists( _appdir + "/../../../source" ):
		BIGWORLD_SOURCE_FOLDER="source"
"""
BIGWORLD_FOLDER = "game"
BIGWORLD_SOURCE_FOLDER = "programming/bigworld"
CLUSTER_BW_ROOT  = TEST_ROOT + "/.."


import xmlconf
#Central path to the binaries


CLUSTER_MACHINES = None
CLUSTER_MACHINES_LOAD = None
CLUSTER_USERNAME = None
CLUSTER_USERNAME_2 = None
CLUSTER_USERNAME_3 = None
CLUSTER_USERNAME_4 = None
CLUSTER_UID = None
CLUSTER_UID_2 = None
CLUSTER_DB_TYPE = None
CLUSTER_DB_HOST = None
CLUSTER_DB_DATABASENAME = None
CLUSTER_DB_USERNAME = None
CLUSTER_DB_PASSWORD = None
CLUSTER_BW_RES_PATH = None
DO_SUDO_COMMANDS = False

WCAPI_USER = None
WCAPI_PASS = None
WCAPI_WCHOST = None
WCAPI_WCPORT = None
WCAPI_SPACE = None

WINDOWS_MOUNT = None

def _parseUserConfigFile( userConfigFile ):
	global CLUSTER_USERNAME
	global CLUSTER_USERNAME_2
	global CLUSTER_USERNAME_3
	global CLUSTER_USERNAME_4
	global CLUSTER_MACHINES
	global CLUSTER_MACHINES_LOAD
	global CLUSTER_BW_ROOT
	global CLUSTER_UID
	global CLUSTER_UID_2
	global DO_SUDO_COMMANDS
	
	try:
		doc = parse( userConfigFile )
	except IOError:
		print "user_config/user_config.xml not found!"
		return

	if doc is None:
		print "failed to parse user_config/user_config.xml!"
		return

	root = None

	for child in doc.childNodes:
		if child.nodeName == "root" and child.nodeType == child.ELEMENT_NODE:
			root = child
			break

	if root is None:
		print "failed to parse user_config/user_config.xml!"
		return

	for child in root.childNodes:
		if child.nodeName == "cluster" and child.nodeType == child.ELEMENT_NODE:
			for i in range(1, 5):
				if i == 1:
					userNameList = child.getElementsByTagName( "user" )
				else:
					userNameList = child.getElementsByTagName( "user%s" % i )
				if userNameList.length >= 1:
					if i == 1:
						CLUSTER_USERNAME = \
							userNameList.item( 0 ).firstChild.nodeValue.strip()
					else:
						globals()["CLUSTER_USERNAME_%s" % i] = \
							userNameList.item( 0 ).firstChild.nodeValue.strip()

			machineList = child.getElementsByTagName( "machines" )
			if machineList.length >= 1:
				CLUSTER_MACHINES = []
				machines = machineList.item( 0 ).getElementsByTagName( "machine" )
				for i in range( machines.length ):
					mname = machines.item( i ).firstChild.nodeValue.strip()
					CLUSTER_MACHINES.append( mname )
					
			machineListLoad = child.getElementsByTagName( "loadmachines" )
			if machineListLoad.length >= 1:
				CLUSTER_MACHINES_LOAD = []
				machines = machineListLoad.item( 0 ).getElementsByTagName( "machine" )
				for i in range( machines.length ):
					mname = machines.item( i ).firstChild.nodeValue.strip()
					CLUSTER_MACHINES_LOAD.append( mname )
				
			

			bwroot = child.getElementsByTagName( "bwRoot" )
			if bwroot.length >= 1:
				CLUSTER_BW_ROOT = \
					bwroot.item( 0 ).firstChild.nodeValue.strip()
			doSudoCommands = child.getElementsByTagName( "dosudocommands" )
			if doSudoCommands.length >= 1:
				DO_SUDO_COMMANDS = True
	try:
		CLUSTER_UID = getpwnam( CLUSTER_USERNAME ).pw_uid
	except:
		CLUSTER_UID = None
	try:
		CLUSTER_UID_2 = getpwnam( CLUSTER_USERNAME_2 ).pw_uid
	except:
		CLUSTER_UID_2 = None

def _setupClusterConfig():
	global CLUSTER_USERNAME
	global CLUSTER_MACHINES
	CLUSTER_USERNAME = getpass.getuser()
	CLUSTER_MACHINES = [ "localhost" ]

	userConfigFile = TEST_ROOT + "/user_config/user_config.xml"

	_parseUserConfigFile( userConfigFile )
				
	clusterConfigFileName = "user_config/server/bw_%s.xml" \
			% CLUSTER_USERNAME 
	clusterConfigName =  TEST_ROOT + "/" + clusterConfigFileName

	try:
		success = xmlconf.readConf( clusterConfigName, sys.modules[__name__],
			{
				'db/type':			 'CLUSTER_DB_TYPE',
				'db/mysql/host': 			 'CLUSTER_DB_HOST',
				'db/mysql/username':		 'CLUSTER_DB_USERNAME',
				'db/mysql/password':		 'CLUSTER_DB_PASSWORD',
				'db/mysql/databaseName':	 'CLUSTER_DB_DATABASENAME',
			} )

	except IOError:
		import traceback
		traceback.print_exc()
		return

	if not success:
		print "Failed to parse %s" % clusterConfigFileName
	
_setupClusterConfig()

try:
	import platform_info
	_platformName = platform_info.findPlatformName()
	SERVER_BINARY_FOLDER = "bin/server/%s/server" % _platformName
	TOOLS_BINARY_FOLDER = "bin/server/%s/tools" % _platformName
except ImportError, e:
	SERVER_BINARY_FOLDER = "bin/Hybrid64"
	TOOLS_BINARY_FOLDER = "tools/server/bin/Hybrid64"

BW_CONFIG = "hybrid"
