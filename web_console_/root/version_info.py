import re
import logging
import sys
import os.path
import subprocess

import bwsetup

bwsetup.addPath( "../.." )

import pycommon.p4_version as P4Version

log = logging.getLogger( __name__ )

# hardbaked value must be kept up to date
# may also be superceded by other sources such as from RPM
_bwVersion = "2.7"
_webConsolePath = os.path.dirname( os.path.abspath( sys.argv[ 0 ] ) )

def loadRPM():

	packageType = "RPM"
	repositoryType = ""
	localRev = ""

	try:
		fp = open( os.path.join( bwsetup.appdir, "package_version" ), "r" )
		buffer = fp.read()

		regSearch = re.search( "Version: (\S+)", buffer )
		try:
			_bwVersion, = regSearch.groups()
			patchReg = re.search( "Patch: (\d+)", buffer )
			try:
				patch, = patchReg.groups()
				versionStrings = [ _bwVersion, patch ]
				_bwVersion = ".".join( versionStrings )
			except:
				pass
		except:
			pass

		regSearch = re.search( "RepositoryType: (\S+)", buffer )
		try:
			repositoryType, = regSearch.groups()
		except:
			pass

		regSearch = re.search( "Revision: (\S+)", buffer )
		try:
			localRev, = regSearch.groups()
		except:
			pass

		if int( localRev ) == 0:
			localRev = ""

		return { "versionNumber": _bwVersion,
				 "packageType": packageType,
				 "repositoryType": repositoryType,
				 "revisionNumber": localRev
		}
		fp.close()
	except:
		pass

	return None
# loadRPM


def loadSVN():
	packageType = ""
	repositoryType = "SVN"
	hasSVNInfo = False
	localRev = ""
	repoLocation = ""
	remoteRev = ""
	modStatus = ""

	try:
		import pysvn

		client = pysvn.Client()
		revEntry = client.info( _webConsolePath )

		localRev = revEntry[ "commit_revision" ].number
		repoLocation = revEntry[ "url" ]
		remoteRev = revEntry[ "revision" ].number

		# the following is required because the status on the directory itself
		# [-1] is never set to modified
		for status in client.status( _webConsolePath ):
			if status["text_status"] == pysvn.wc_status_kind.modified:
				modStatus = "Modified"

		# if we have made it this far then modStatus is no longer unknown
		if modStatus is not "Modified":
			modStatus = "Unmodified"

		hasSVNInfo = True
	except:
		pass
		# no pysvn available

	if not hasSVNInfo:

		try:
			# try using shell system call
			svnProc = subprocess.Popen( ["svn", "info", _webConsolePath],
				stdout = subprocess.PIPE, stderr = subprocess.PIPE )
			out, err = svnProc.communicate()
			if svnProc.returncode > 0:
				return None

			regSearch = re.search( "Last Changed Rev: (\d+)", out )
			try:
				localRev, = regSearch.groups()
			except:
				pass

			regSearch = re.search( "URL: (\S+)", out )
			try:
				repoLocation, = regSearch.groups()
			except:
				pass

			regSearch = re.search( "Revision: (\d+)", out )
			try:
				remoteRev, = regSearch.groups()
			except:
				pass

			hasSVNInfo = True
		except:
			pass

	if not hasSVNInfo:
		return None

	return { "versionNumber": _bwVersion,
 			 "packageType": packageType,
 			 "repositoryType": repositoryType,
			 "revisionNumber": str( localRev ),
			 "remoteRevisionNumber": str( remoteRev ),
			 "modStatus": modStatus,
			 "repositoryLocation": repoLocation
	}
# loadSVN


def loadP4():
	try:
		versionInfo = P4Version.loadVersionInfo()
	except:
		return None

	if not versionInfo:
		return None

	# If there are any diffs within the WebConsole path then it has
	# been modified
 	p4Proc = subprocess.Popen( ["p4", "diff", "-f", "-sa", _webConsolePath + "/..."],
 		stdout = subprocess.PIPE, stderr = subprocess.PIPE )
 	out, err = p4Proc.communicate()

	devConfig = _webConsolePath + "/dev.cfg"
	diffFiles = out.split( os.linesep )
	nonConfigFiles = [line for line in diffFiles if line != devConfig and len(line)]


	# append locally known information to the dict
	versionInfo[ 'versionNumber' ] = _bwVersion
	versionInfo[ 'repositoryType' ] = "Perforce"

 	if nonConfigFiles:
 		versionInfo[ 'modStatus' ] = "Modified"
 	else:
 		versionInfo[ 'modStatus' ] = "Unmodified"

	return versionInfo
# loadP4


def load():
	log.info( "Loading version info" )

	versionInfo = loadRPM()

	if not versionInfo:
		versionInfo = loadSVN()

	if not versionInfo:
		versionInfo = loadP4()

	if not versionInfo:
		log.info( "Unable to load version info, using hardbaked version " +
				_bwVersion )
		return { "versionNumber": _bwVersion }

	return versionInfo
# load


# version_info.py
