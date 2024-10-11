import encodings
import json
import logging
import sys

import BigWorld


class BWLogger( logging.Logger ):
	"""This class extends the logging.Logger class to provide BigWorld specific
	log level support."""

	TRACE = logging.DEBUG - 1
	NOTICE = logging.INFO + 1
	HACK = logging.CRITICAL + 1

	def __init__( self, name, level = logging.NOTSET ):
		logging.Logger.__init__( self, name, level )


	def trace( self, msg, *args, **kw ):
		"""Trace messages are the lowest priority log level within the BigWorld
		Technology ecosystem"""

		if self.isEnabledFor( BWLogger.TRACE ):
			self._log( BWLogger.TRACE, msg, args, **kw )


	def notice( self, msg, *args, **kw ):
		"""Notice messages are listed as a severity between an INFO and 
		a WARNING."""

		if self.isEnabledFor( BWLogger.NOTICE ):
			self._log( BWLogger.NOTICE, msg, args, **kw )


	def hack( self, msg, *args, **kw ):
		"""Hack messages are the highest priority log level within the BigWorld
		Technology ecosystem"""

		if self.isEnabledFor( BWLogger.HACK ):
			self._log( BWLogger.HACK, msg, args, **kw )


# This dictionary maps a log level to a specific message handler function.
logLevelToBigWorldFunction = {
	logging.NOTSET: BigWorld.logTrace,
	BWLogger.TRACE: BigWorld.logTrace,

	logging.DEBUG: BigWorld.logDebug,
	logging.INFO: BigWorld.logInfo,
	BWLogger.NOTICE: BigWorld.logNotice,

	logging.WARN: BigWorld.logWarning,
	logging.WARNING: BigWorld.logWarning,

	logging.ERROR: BigWorld.logError,

	logging.CRITICAL: BigWorld.logCritical,
	logging.FATAL:    BigWorld.logCritical,

	BWLogger.HACK: BigWorld.logHack
}


class BWLogRedirectionHandler( logging.Handler ):
	"""This class extends the logging Handler class to intercept a log message
	and redirect it to the BigWorld log message handlers for transport to
	MessageLogger."""

	def __init__( self ):
		logging.Handler.__init__( self )


	def emit( self, record ):

		logCategory = record.name.encode( sys.getdefaultencoding() )

		# Test whether the log message has a valid format string / arg list
		msg = record.getMessage()
		finalMessage = msg.encode( sys.getdefaultencoding() )

		if hasattr( record, "metadata" ):
			logMetaData = json.dumps( record.metadata )
		else:
			logMetaData = None

		bwInternalLogFunction = logLevelToBigWorldFunction[ record.levelno ]

		bwInternalLogFunction( logCategory, finalMessage, logMetaData )

		# TODO: When we decide to perform Python argument parsing we will need
		#       to process the message and argument list separately as such.
		#bwInternalLogFunction( record.msg, record.args )



_bwRedirectionHandler = None


def init():
	"""Initialise the BWLogging module."""

	global _bwRedirectionHandler
	_bwRedirectionHandler = BWLogRedirectionHandler()

	# Define the default Logger class to use for any logs generated.
	logging.setLoggerClass( BWLogger )

	# Create a new log level for any BigWorld levels that don't exist in the
	# base logging module.
	logging.addLevelName( BWLogger.TRACE, "TRACE" )
	logging.addLevelName( BWLogger.NOTICE, "NOTICE" )
	logging.addLevelName( BWLogger.HACK, "HACK" )

	# Attach our custom message handler to the root logger and set the minimum
	# severity level to be logged as BigWorld's TRACE severity.
	rootLogger = logging.getLogger()
	rootLogger.addHandler( _bwRedirectionHandler )
	rootLogger.setLevel( BWLogger.TRACE )

	# Redirect any Python-raised warnings to py.warnings category
	logging.captureWarnings( True )


# BWLogging.py
