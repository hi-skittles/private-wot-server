"""
Collection of decorators for method throttling
"""

import BigWorld
import logging

throttleLog = logging.getLogger( "Security" )

# Hard Threshold decorators

class _HardThreshold( object ):
	USE_CALLER_ID = False

	def __init__( self, warningTime = 0.0, dropTime = 0.0 ):
		self._warnTime = warningTime
		self._dropTime = dropTime


	def __call__( self, func ):
		if 0.0 < self._warnTime and self._warnTime < self._dropTime:
			throttleLog.warn( "Hard threshold decorator on method '%s': " + \
					"warningTime(%f) < dropTime(%f)! warningTime ignored.", \
				func.__name__, self._warnTime, self._dropTime )
			self._warnTime = 0.0 

		def wrapper( *args, **kwArgs ):
			owner = args[ 0 ]

			if self.USE_CALLER_ID:
				callerID = args[ 1 ]
			else:
				callerID = -1

			lastTime = self.lastTime( owner, func.__name__, callerID )
			if lastTime >= 0:
				dt = BigWorld.time() - lastTime
				if dt < self._dropTime:
					self.printOnDrop( owner, callerID, func.__name__ )
					return None
				elif dt < self._warnTime:
					self.printOnWarning( owner, callerID, func.__name__ )

			return func( *args, **kwArgs )

		return wrapper


	def printOnWarning( self, owner, callerID, funcName ):
		if callerID < 0:
			callerID = owner.id
		throttleLog.warn( "Method calls to %s(%d) from %d are too frequent", \
							funcName, owner.id, callerID )


	def printOnDrop( self, owner, callerID, funcName ):
		if callerID < 0:
			callerID = owner.id
		throttleLog.warn( "Dropped method call to %s(%d) from %d due to throttling", \
							funcName, owner.id, callerID )


class hardThresholdCell( _HardThreshold ):
	USE_CALLER_ID = True

	def lastTime( self, owner, funcName, callerID ):
		lastTime = owner.throttleFilterHardThresholdCell.get( funcName )
		if lastTime is None:
			lastTime = -1.0

		owner.throttleFilterHardThresholdCell[ funcName ] = BigWorld.time()

		return lastTime


class hardThresholdCellAllClients( hardThresholdCell ):

	LAST_CLEANING_TIME_KEY = "$lastCleaningTime"

	def __init__( self, 
					warningTime = 0.0,
					dropTime = 0.0,
					cleanTimeout = 12.0,	# Number of seconds after which the
											# history will be cleaned from old 
											# entries.
					flushThreshold = 64 ):	# max number of callers per method after
											# which the history will be wiped out 
											# (all but the last caller)
		hardThresholdCell.__init__( self, warningTime, dropTime )
		cleanTimeout = max( cleanTimeout, warningTime, dropTime )
		self._cleanTimeout = cleanTimeout
		self._flushThreshold = flushThreshold


	def lastTime( self, owner, funcName, callerID ):
		context = owner.throttleFilterHardThresholdCell
		calls = context.get( funcName )
		if calls is None:
			calls = {}
			context[ funcName ] = calls

		currTime = BigWorld.time()

		lastCallerTime = calls.get( callerID, -1 )

		lastCleaningTime = calls.get( self.LAST_CLEANING_TIME_KEY )
		if lastCleaningTime is None:
			lastCleaningTime = currTime
			calls[ self.LAST_CLEANING_TIME_KEY ] = currTime

		if currTime - lastCleaningTime > self._cleanTimeout:
			# do the cleanup here...
			keysToDel = [ k for k, v in calls.iteritems() \
							if currTime - v > self._warnTime ]
			for k in keysToDel:
				del calls[ k ]
			calls[ self.LAST_CLEANING_TIME_KEY ] = currTime
			# throttleLog.warn( "CLEANED method calls to %s(%d)!", \
			#					funcName, owner.id )


		if len(calls) > self._flushThreshold:
			calls.clear()
			calls[ self.LAST_CLEANING_TIME_KEY ] = currTime
			throttleLog.warn( "FLUSHED method calls to %s(%d)" + \
								" due to history being too big!", \
							funcName, owner.id )


		calls[ callerID ]  = currTime

		return lastCallerTime


class hardThresholdBase( _HardThreshold ):

	def lastTime( self, owner, funcName, callerID ):
		lastTime = owner.throttleFilterHardThresholdBase.get( funcName )
		if lastTime is None:
			lastTime = -1.0

		owner.throttleFilterHardThresholdBase[ funcName ] = BigWorld.time()

		return lastTime


# ThrottledMethods.py

