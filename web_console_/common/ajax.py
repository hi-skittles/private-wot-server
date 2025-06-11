import turbogears
import traceback
import sys
import time

from StringIO import StringIO
from turbogears import exception_handler

import bwsetup; bwsetup.addPath( "../.." )
import util

import logging
log = logging.getLogger( __name__ )


# Status codes to be returned to the client browser
OK = 0
ERROR = 1
EXCEPTION = 2

# A dictionary of stack traces.  Note that at the moment this is never cleared,
# so is technically a memory leak in proportion to the number of uncaught
# exceptions being generated.
exceptions = {}
exceptions[ "currenum" ] = 0

def expose( f, exposeParams = dict( format = "json" ) ):
	"""
	A replacement for turbogears.expose() that does automatic status pass-back
	to the client browser so AJAX errors can be detected there as well as in the
	web console logs.

	All the app level code needs to know is that it can pass back JSON by
	returning a dictionary, it can cause a info dialog to be displayed in the
	client browser by returning a string, or it can cause an error dialog to be
	displayed by raising an Error (see below).  Uncaught exceptions in the app
	code will cause a stack trace to be displayed in a new window on the client.

	Note that this mechanism reserves several names in the returned dictionary,
	all of which start with an underscore.  Any app-level code that uses this
	should avoid passing back parameters that start with an underscore.
	"""

	@turbogears.expose( **exposeParams )
	@util.unicodeToStr
	def execute( *args, **kw ):

		try:
			ret = f( *args, **kw )

			# Returning None or nothing is the same as returning dict()
			if ret is None:
				ret = {}

			# If the app code returns a string, we will display that message on
			# the client in a dialog
			if type( ret ) == str or type( ret ) == unicode:
				ret = dict( _message = ret )

			# If the app code doesn't explicitly specify status, we assume it's
			# OK.  In general the app code shouldn't be specifying the status.
			if "_status" not in ret:
				ret[ "_status" ] = OK

			return ret

		# These errors aren't so bad
		except Error, e:
			return dict( _status = ERROR, _error = e.error,
						 _details = e.details )

		# Other exceptions are bad, and will redirect to a stack trace
		except Exception, e:

			trace = StringIO()
			traceback.print_exc( file=trace )

			# Save the exception information
			enum = exceptions[ "currenum" ]
			enum += 1
			if enum >= 128:
				enum = 1
			exceptions[ "currenum" ] = enum

			errorMsg = str( sys.exc_value )
			exceptions[ enum ] = ( errorMsg, trace.getvalue(), time.time() )

			# Log an error
			log.error( "* Exception caught in exposed AJAX method *\n%s",
					   trace.getvalue() )

			# Pass a url to the exception information back
			url = turbogears.url( "/exception", enum = enum )
			return dict( _status = EXCEPTION, _redirect = url, error = errorMsg )

	return execute


class Error( Exception ):
	"""
	What you should raise when you want to pop up an error dialog in the client
	web browser, but don't want to redirect them to a stack trace.  Basically,
	this should be used for runtime, not code, errors.
	"""

	def __init__( self, error, details = [] ):
		Exception.__init__( self, error )
		self.error = error

		if type( details ) == list:
			self.details = details
		else:
			self.details = [details]
