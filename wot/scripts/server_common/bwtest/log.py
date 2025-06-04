"""
This module provides logging functonality by using the python logging
library to be used in auto tests (in particular, in test cases).  

Typical usage of this module would be:

from bwtest import log

log.warning( 'Help me!' )
"""

import sys
import logging

# Supported log levels

DEBUG = logging.DEBUG			# used in TestCase's
INFO = logging.INFO				# used in bwtest, primitives, helpers
WARNING = logging.WARNING		# used in bwtest, primitives, helpers 
PROGRESS = logging.WARNING+1;	# used in test runner to notify on progress
ERROR = logging.ERROR			# used in bwtest, primitives, helpers
CRITICAL = logging.CRITICAL		# TODO: raise an exception

logging.addLevelName( PROGRESS, "PROGRESS" )

choicesMap = {
	"debug": DEBUG,
	"info": INFO,
	"warning": WARNING,
	"progress": PROGRESS,
	"error": ERROR,
	"critical": CRITICAL,
	}


class _CleanFormatter( logging.Formatter ):
	"""Formatting class for log messages
	"""
	def __init__( self ):
		logging.Formatter.__init__( self )

	def format( self, record ):
		return "%-10s[%s] %s" % (logging.getLevelName( record.levelno ),
								record.name,
								record.getMessage())


# StreamHandler that terminates process on CRITICAL
class _StreamHandler( logging.StreamHandler ):

	def __init__( self, strm = sys.stdout ):
		logging.StreamHandler.__init__( self, strm )

	def emit( self, record ):
		return logging.StreamHandler.emit( self, record )


console = _StreamHandler()

console.setFormatter( _CleanFormatter() )

logger = logging.getLogger( "bwtest" )
rootlogger = logging.getLogger()

rootlogger.addHandler( console )
logger.setLevel( WARNING )
rootlogger.setLevel( WARNING )


def setLevel( level ):
	"""Set logging level
	@param level: Level to set. Possible levels can be found in choicesMap
	"""
	rootlogger.setLevel( level )
	logger.setLevel( level )

# Hook in funcs for ease of use
def debug( msg, *args, **kw ): 
	"""Debug level message.
	@param msg: Message to log
	"""
	return logger.debug( msg, *args, **kw )

def info( msg, *args, **kw ): 
	"""Info level message.
	@param msg: Message to log
	""" 
	return logger.info( msg, *args, **kw )

def warning( msg, *args, **kw ): 
	"""Warninglevel message.
	@param msg: Message to log
	""" 
	return logger.warning( msg, *args, **kw )

def progress( msg, *args, **kw ): 
	"""Progress level message.
	@param msg: Message to log
	"""
	return logger.log( PROGRESS, msg, *args, **kw )

def error( msg, *args, **kw ): 
	"""Error level message.
	@param msg: Message to log
	"""
	return logger.error( msg, *args, **kw )

def critical( msg, *args, **kw ): 
	"""Critical  level message.
	@param msg: Message to log
	"""
	return logger.critical( msg, *args, **kw )

