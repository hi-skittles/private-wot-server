import imp
import os.path
import BigWorld

import srvtest
from snippet_decorator import testSnippet


# -----------------------------------------------------------------------------
# Module loader

@testSnippet
def loadModule( path ):
	mpath, mname = os.path.split( path )
	try:
		file, filename, data = imp.find_module( mname, [ mpath ] )
	except ImportError:
		return False

	if file is None:
		return False

	mod = None
	try:
		mod = imp.load_module( mname, file, filename, data)
	except ImportError:
		pass
	finally:
		file.close()

	return mod is not None

	
# -----------------------------------------------------------------------------
# Has this app started?

@testSnippet
def hasAppStarted():
	return BigWorld.hasStarted()
