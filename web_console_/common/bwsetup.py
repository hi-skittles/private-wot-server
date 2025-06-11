import os
import sys

# Do this as early as possible in case someone does an os.chdir() at some point
appdir = os.path.dirname( os.path.abspath( __file__ ) )

def addPath( relpath, pos = None ):
	"""
	relpath should be the relative path to bigworld/tools/server for this
	application.  Pass 'pos' to insert this into sys.path at the specified
	index, useful if you want to make sure a custom library is loaded ahead of
	system libraries with the same name.
	"""

	root = os.path.abspath( appdir + "/" + relpath )
	if root not in sys.path:
		if pos is None:
			sys.path.append( root )
		else:
			sys.path.insert( pos, root )
