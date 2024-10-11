import ResMgr
from bwdebug import TRACE_MSG
from functools import partial

try:
	# Sometimes __builtins__ acts like a dict, sometimes a module...
	orig_open = __builtins__[ "open" ]
except TypeError, e:
	orig_open = __builtins__.open

@partial
def bwResRelativeOpen( name, *args ):
	"""
	This method has been decorated with 'partial' to avoid using a function as 
	a bound method when stored as a class attribute (see WOWP-638). """
	try:
		name = ResMgr.resolveToAbsolutePath( name )
	except Exception, e:
		raise IOError( 2, str(e) )

	return orig_open( name, *args )


# This function will modify the built in open() method so that relative paths
# are opened relative to the res path.
def monkeyPatchOpen():
	TRACE_MSG( "BWUtil.monkeyPatchOpen: Patching open()" )

	try:
		__builtins__[ "open" ] = bwResRelativeOpen
	except TypeErorr, e:
		__builtins__.open = bwResRelativeOpen

# BWUtil.py
