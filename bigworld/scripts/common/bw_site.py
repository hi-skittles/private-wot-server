# This module is automatically imported.

# If you change the default encoding, you should also change this for WebConsole
# in bigworld/tools/server/web_console/common/encoding.py
DEFAULT_ENCODING = "utf-8"
# DEFAULT_ENCODING = "gb18030"

# Get our hooks into Python's log system
import BWLogging
BWLogging.init()

# Ensure 'open' goes through ResMgr
import BigWorld
if not BigWorld.component.startswith( 'process_defs' ):
	import BWUtil
	BWUtil.monkeyPatchOpen()
	
	# In order for profiling to function across multiple threads we need to
	# monkey patch the threading bootstrap
	import threading
	orig_bootstrap = threading.Thread._Thread__bootstrap
	
	def hooked_bootstrap( self ):
		BigWorld.__onThreadStart( self.name )
		orig_bootstrap( self )
		BigWorld.__onThreadEnd()
	
	threading.Thread._Thread__bootstrap = hooked_bootstrap
	



# Setup extra builtin functions, copied from site.py
import __builtin__

import pydoc


class _Helper(object):
	"""Define the built-in 'help'.
	This is a wrapper around pydoc.help (with a twist).

	"""

	def __repr__(self):
		return "Type help() for interactive help, " \
			   "or help(object) for help about object."
	def __call__(self, *args, **kwds):
		return pydoc.help(*args, **kwds)


def sethelper():
	__builtin__.help = _Helper()


# Set up the default encoding, roughly copied from site.py
import encodings
import sys

def setDefaultEncoding():
	if hasattr( sys, "setdefaultencoding" ):
		sys.setdefaultencoding( DEFAULT_ENCODING )
		del sys.setdefaultencoding

		import logging
		configLog = logging.getLogger( "Config" )
		configLog.info( "Default encoding set to %s", sys.getdefaultencoding() )


# Clean up sys.paths and add site-packages, copied from site.py
import os
import traceback

def makepath(*paths):
	dir = os.path.join(*paths)
	try:
		dir = os.path.abspath(dir)
	except OSError:
		pass
	return dir, os.path.normcase(dir)


def removeduppaths():
	""" Remove duplicate entries from sys.path along with making them
	absolute"""
	# This ensures that the initial path provided by the interpreter contains
	# only absolute pathnames, even if we're running from the build directory.
	L = []
	known_paths = set()
	for dir in sys.path:
		# Filter out duplicate paths (on case-insensitive file systems also
		# if they only differ in case); turn relative paths into absolute
		# paths.
		dir, dircase = makepath(dir)
		if not dircase in known_paths:
			L.append(dir)
			known_paths.add(dircase)
	sys.path[:] = L
	return known_paths


def getsitepackages():
	"""Returns a list containing all global site-packages directories
	(and possibly site-python).

	For each directory present in the global ``PREFIXES``, this function
	will find its `site-packages` subdirectory depending on the system
	environment, and will return a list of full paths.
	"""
	sitepackages = []
	seen = set()

	# customised for BigWorld: Just pull in any site-packages directory
	# in a sys.path directory
	for prefix in sys.path:
		if not prefix or prefix in seen:
			continue
		seen.add(prefix)

		sitepackages.append(os.path.join(prefix, "site-packages"))
	return sitepackages


def _init_pathinfo():
	"""Return a set containing all existing directory entries from sys.path"""
	d = set()
	for dir in sys.path:
		try:
			if os.path.isdir(dir):
				dir, dircase = makepath(dir)
				d.add(dircase)
		except TypeError:
			continue
	return d


def addpackage(sitedir, name, known_paths):
	"""Process a .pth file within the site-packages directory:
	   For each line in the file, either combine it with sitedir to a path
	   and add that to known_paths, or execute it if it starts with 'import '.
	"""
	if known_paths is None:
		_init_pathinfo()
		reset = 1
	else:
		reset = 0
	fullname = os.path.join(sitedir, name)
	try:
		f = open(fullname, "rU")
	except IOError:
		return
	with f:
		for n, line in enumerate(f):
			if line.startswith("#"):
				continue
			try:
				if line.startswith(("import ", "import\t")):
					exec line
					continue
				line = line.rstrip()
				dir, dircase = makepath(sitedir, line)
				if not dircase in known_paths and os.path.exists(dir):
					sys.path.append(dir)
					known_paths.add(dircase)
			except Exception as err:
				print >>sys.stderr, "Error processing line {:d} of {}:\n".format(
					n+1, fullname)
				for record in traceback.format_exception(*sys.exc_info()):
					for line in record.splitlines():
						print >>sys.stderr, '  '+line
				print >>sys.stderr, "\nRemainder of file ignored"
				break
	if reset:
		known_paths = None
	return known_paths


def addsitedir(sitedir, known_paths=None):
	"""Add 'sitedir' argument to sys.path if missing and handle .pth files in
	'sitedir'"""
	if known_paths is None:
		known_paths = _init_pathinfo()
		reset = 1
	else:
		reset = 0
	sitedir, sitedircase = makepath(sitedir)
	if not sitedircase in known_paths:
		sys.path.append(sitedir)		# Add path component
	try:
		names = os.listdir(sitedir)
	except os.error:
		return
	dotpth = os.extsep + "pth"
	names = [name for name in names if name.endswith(dotpth)]
	for name in sorted(names):
		addpackage(sitedir, name, known_paths)
	if reset:
		known_paths = None
	return known_paths


def addsitepackages(known_paths):
	"""Add site-packages (and possibly site-python) to sys.path"""
	for sitedir in getsitepackages():
		if os.path.isdir(sitedir):
			addsitedir(sitedir, known_paths)

	return known_paths


def setUpPaths():
	known_paths = removeduppaths()
	known_paths = addsitepackages(known_paths)


def main():
	sethelper()
	setDefaultEncoding()
	setUpPaths()

	import bwpydevd
	bwpydevd.startDebug( isStartUp = True )

main()

# end of site.py work-alikes

import bwdeprecations

from bwdebug import NOTICE_MSG
try:
	import BWAutoImport
except ImportError, e:
	NOTICE_MSG( "bw_site.py failed to import BWAutoImport: %s\n" % ( e, ) )


# Override Twisted's default reactor, selectreactor, with our BWTwistedReactor.
# This ensures the only reactor installed is BWTwistedReactor.
try:
	import BWTwistedReactor
	import twisted.internet.selectreactor
	twisted.internet.selectreactor = BWTwistedReactor
except: pass

# bw_site.py
