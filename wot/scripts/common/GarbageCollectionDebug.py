"""
This is an example of how to disable/enable garbage collection, and how to
activate debugging. Debugging output is sent to stdout.

By default, all components that use Python have its garbage collection disabled.
However, script developers may find garbage collection to be useful to identify
leaks due to cyclical memory references.

More information about how the Python garbage collection facility works can be
found in the Python documentation for the gc module.
http://docs.python.org/library/gc.html

More information about BigWorld Technology's use of Python and C can be found
in bigworld/doc/python_and_c.pdf.

This script can be used in the personality script (BaseApp, CellApp or client)
to activate the functions on BigWorld component shutdown.

It also imports things on demand instead of at the top of the file to try and
minimise the number of imported modules (which may then import more modules)
which would give false results when testing memory allocations.
"""

# Log file to dump to
DUMP_PATH = "gcDump.log"

# Limit length of sequences being dumped to the log
LIMIT_LEN = False

# Length limit for sequences being dumped to log
# Only dump [0..MAX_LEN] elements
MAX_LEN = 5

# Depth limit for sequences within sequences being dumped to log
MAX_DEPTH = 1

# Create a test leak
TEST_SIMPLE_LEAK = False
TEST_COMPLEX_LEAK = False

try:
	import gc
	# These are documented in the gc module section of the Python manual
	#GC_DEBUG_FLAGS =  gc.DEBUG_STATS | gc.DEBUG_COLLECTABLE | \
	#	gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS

	# DEBUG_LEAK
	# The debugging flags necessary for the collector to print information
	# about a leaking program
	# (equal to DEBUG_COLLECTABLE | DEBUG_UNCOLLECTABLE | DEBUG_INSTANCES
	# | DEBUG_OBJECTS | DEBUG_SAVEALL).

	# DEBUG_STATS
	# Print statistics during collection.
	# This information can be useful when tuning the collection frequency.
	#GC_DEBUG_FLAGS = gc.DEBUG_LEAK
	GC_DEBUG_FLAGS = gc.DEBUG_SAVEALL

except ImportError:
	GC_DEBUG_FLAGS = 0

def gcEnable():
	"""
	Enable garbage collection. Raises a SystemError if garbage collection is
	not supported.
	"""
	try:
		import gc
		gc.enable()
	except ImportError:
		raise RuntimeError, "Garbage collection is not supported"

def gcDisable():
	"""
	Disable garbage collection.
	"""
	try:
		import gc
		gc.disable()
	except ImportError:
		# do nothing
		return

def gcDebugEnable():
	"""
	Call this function to enable garbage collection debugging. Prints a warning
	message if there is no support for garbage collection.
	"""
	try:
		import gc
		gc.set_debug( GC_DEBUG_FLAGS )
	except ImportError:
		from bwdebug import ERROR_MSG
		ERROR_MSG( "Could not import gc module; " +
			"garbage collection support is not compiled in" )

def gcIsLeakDetect():
	"""
	Check if leak detection is on.
	"""
	try:
		import gc
		if ( gc.isenabled() and ( gc.get_debug() & gc.DEBUG_LEAK ) ) > 0:
			return True

	except ImportError:
		from bwdebug import ERROR_MSG
		ERROR_MSG( "Could not import gc module; "
			"garbage collection support is not compiled in" )

	return False

def gcDump( doFullCheck = False, logName = DUMP_PATH ):
	"""
	Performs a garbage collect and then print a dump of what has been
	collected.
	
	doFullCheck if True, do a collect and iterate over collected garbage
	and print info.
	Otherwise, do a collect and just print the number of objects collected.
	logName the name of the file to log to.
	"""

	from bwdebug import DEBUG_MSG
	from bwdebug import ERROR_MSG

	# Import gc
	try:
		import gc
	except ImportError:
		ERROR_MSG( "Could not import gc module; " +
			"garbage collection support is not compiled in" )
		return

	# Create test leaks
	createTestLeaks()

	# Collect and log
	leakCount = 0

	# Put the garbage collector in debug mode
	# (gc does not have to be enabled)
	gcDebugEnable()

	# Do a collection
	# This will collect junk into gc.garbage
	DEBUG_MSG( "Forcing a garbage collection..." )
	leakCount = gc.collect()

	# Iterate over list and log info about objects
	if doFullCheck:
	
		# Copy gc.garbage so that we can safely iterate over it
		copy = gc.garbage[:]
	
		# Clear the list
		del gc.garbage[:]

		try:
			# Open log file
			# (do this after collection - keep out of log)
			file = open( logName, "w" )
	
			# Print total amount of garbage
			s = "Total garbage: %u" % ( leakCount, )
			DEBUG_MSG( s )
			file.write( s + "\n" )
	
			# Print list of garbage
			if len( copy ) > 0:
				DEBUG_MSG(
					"Writing objects in garbage to file: \"%s\"" % ( logName, )  )
				file.write( "Objects in garbage:\n" )
	
			# Iterate through copy of gc.garbage
			i = 0
			for g in copy:
	
				# Print item info
				try:
	
					# Index in garbage
					s = "Garbage item %u\n" % ( i, )
	
					# Get object info
					s += getObjectData( g )
	
					# Get referrer info
					# Ignore any references from "gc.garbage" or "copy"
					s += getObjectReferrers( g, [ gc.garbage, copy ] )
	
					# Add a new line at the start
					# Print message
					file.write( "\n" + s )
	
					# Try to flush output buffer in case it's getting saturated
					file.flush()
	
				# Could be a problem if garbage list is getting edited
				# while we are iterating over it
				# Or when using gc.DEBUG_SAVEALL and not gc.DEBUG_LEAK
				except ReferenceError, e:
					s = "Error: Object referenced in garbage list no longer exists: %s" % ( e, )
					file.write( "\n" + s )
					ERROR_MSG( s )
	
				# Increment item number
				i += 1
	
			# Close log
			file.flush()
			file.close()

		# Error writing to disk
		# Possibly output has grown too big or a
		# problem with the output redirection during shutdown
		except IOError, e:
			# Something wrong with file
			# Can only print error to console
			ERROR_MSG( e )
	
		# Log failed
		except:
			# Print error to log
			file.write( "Error printing garbage dump, see console.\n" )
			ERROR_MSG( "Error printing garbage dump." )
	
			# Close log
			file.flush()
			file.close()

			# Raise
			raise
			
	# Not doFullCheck
	# Do nothing with list
	else:
		# Clear the list
		del gc.garbage[:]

	return leakCount

class TestLeak:
	pass

def createTestLeaks():

	
	if TEST_SIMPLE_LEAK:
		createBasicLeak()

	if TEST_COMPLEX_LEAK:
		createComplexLeak()
		
def createBasicLeak():
	'''
	For testing if the garabage collection log works.

	Creates a circular reference with a self-referencing object.

	So there should be two items found in gc.garbage:
	- the "ref" instance object
	- the dictionary of "ref", which contains "selfref"
	'''
	from bwdebug import DEBUG_MSG
	DEBUG_MSG( "Creating a simple test leak.." )

	ref = TestLeak()
	ref.selfRef = ref
	ref = None

def createComplexLeak():
	'''
	For testing if the garabage collection log works.
	
	Creates a reference cycle with three objects.
	
	There should be six items found in gc.garbage:
	- the "refChain" instance object
	- the dictionary of "refChain", which contains "badRefStart"
	- the "refLink1" instance object
	- the dictionary of "refLink1", which contains "badRefMiddle"
	- the "refLink2" instance object
	- the dictionary of "refLink2", which contains "badRefEnd"
	'''
	from bwdebug import DEBUG_MSG
	DEBUG_MSG( "Creating a complex test leak.." )

	refChain = TestLeak()
	refLink1 = TestLeak()
	refLink2 = TestLeak()
	refChain.badRefStart = refLink1
	refLink1.badRefMiddle = refLink2
	refLink2.badRefEnd = refChain
	refChain = None
	refLink1 = None
	refLink2 = None
	
def getObjectData( obj, indent = "" ):
	"""
	Get info about a given object.
	Name, type etc.
	Return as a string.
	"""

	result = ""

	result += ( "%sObject id %u\n" % ( indent, id( obj ) ) )

	# Try to print name
	try:
		result += ( "%s name: %s\n" % ( indent, obj.__class__.__name__ ) )
	except AttributeError:
		result += ( "%s name: no name\n" % ( indent, ) )

	# Print type
	result += ( "%s type: %s\n" % ( indent, type( obj ) ) )

	# Try to get length
	# (for objects that have len())
	try:
		# Print length
		result += ( "%s len : %u\n" % ( indent, len( obj ) ) )
	except AttributeError:
		result += ( "%s len : no length\n" % ( indent, ) )
	except TypeError:
		result += ( "%s len : no length\n" % ( indent, ) )

	# Print items in sequence or string
	result += getContents( obj, indent )

	# Try to print size
	try:
		import sys
		result += ( "%s bytes: %u\n" % ( indent, sys.getsizeof( obj ) ) )
	except ImportError:
		result += ( "%s bytes: could not get size\n" % ( indent, ) )

	return result

def getContents( obj, indent = "" ):
	"""
	Get a string representing an object or the first few items in a sequence.
	"""

	result = ""

	# Try to print items in sequence
	try:
		# Try to import pretty printer
		import pprint

		# Limit depth of items nested in lists
		pp = pprint.PrettyPrinter( depth=MAX_DEPTH )

		# Only print up to first MAX_LEN elements
		if LIMIT_LEN:
			if len( obj ) <= MAX_LEN:
				# Pretty Print
				result += ( "%s contents: %s\n" % ( indent, pp.pformat( obj ) ) )
			else:
				# Slice off first MAX_LEN elements
				short = obj[:MAX_LEN]
				# Pretty print
				result += ( "%s partial contents (first %u): %s ...\n" % ( indent, MAX_LEN, pp.pformat( short ) ) )

		# Print entire list
		else:
			# Pretty Print
			result += ( "%s contents: %s\n" % ( indent, pp.pformat( obj ) ) )

	except ImportError, e:
		# No pretty printer
		from bwdebug import ERROR_MSG
		ERROR_MSG( "Error: could not import pprint: %s" % ( e, ) )
		raise

	# len() failed
	# Looks like it wasn't a sequence
	# Print string instead
	except AttributeError:
		result += ( "%s str : %s\n" % ( indent, pp.pformat( obj ) ) )
	except TypeError:
		result += ( "%s str : %s\n" % ( indent, pp.pformat( obj ) ) )

	return result

def getObjectReferrers( obj, ignore ):
	"""
	Get info about what objects are referring to a given object.
	Return info as a string.
	Ignore referrers in the "ignore" list.
	"""

	result = ""

	# Try to print number of referrers
	try:
		import sys
		# Subtract 1 because sys.getrefcount counts its own
		# reference to the object
		refCount = sys.getrefcount( obj )
		result += ( " sys.getrefcount: %u\n" % ( refCount, ) )
	except:
		pass

	# Try to print referrers
	try:
		referrers = gc.get_referrers( obj )
		result += ( " gc.get_referrers (%u):\n" % ( len( referrers ), ) )

		# Count which referrer we're up to
		i = 0
		for r in referrers:
			# Print referrer
			try:
				# Print index
				result += ( " ->(referrer %u)\n" % ( i, ) )

				# Print info
				if r not in ignore:
					result += getObjectData( r, " -> " )
				else:
					result += " -> reference from gc.garbage list (ignore)\n"

			except:
				print "Error getting referrer"

			# Update count
			i += 1

	except:
		result += "Error getting referrers"

	return result

#GarbageCollectionDebug.py
