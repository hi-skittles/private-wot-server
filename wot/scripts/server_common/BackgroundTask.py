"""
BackgroundTask provides a set of classes to offload tasks from the main
python thread within a BigWorld process. This allows blocking operations
such as file access or network operations to databases to be performed in
an asynchronous manner.

In order to use background tasks, a task manager needs to be started which
is responsible for managing a pool of threads that the tasks will be
executed in. The number of threads used can be controlled per manager
instance.

EXAMPLE:

class MyTask( BackgroundTask.BackgroundTask ):
	def doBackgroundThreadTask( self, mgr, threadData ):
		print 'Hello from the background thread'
		mgr.addMainThreadTask( self )

	def doMainThreadTask( self, mgr ):
		print 'Hello from the main thread'


def init():
	...
	threadManager = BackgroundTask.Manager()
	threadManager.startThreads( 1 )

def main():
	...
	threadManager.addBackgroundTask( MyTask() )

def fini():
	...
	threadManager.stopAll()
"""

import BigWorld
import thread
import os
import threading
import traceback
import time
from Queue import Queue

class Stats( object ):
	def __init__( self, needsLock = False ):
		self.completedJobs = 0
		self.longestJobClass = ""
		self.longestJobTime = 0.0
		if needsLock:
			lock = thread.allocate_lock()
			self.acquire = lock.acquire
			self.release = lock.release
		else:
			self.acquire = lambda: None
			self.release = lambda: None


	def onJobCompleted( self, elapsedTime, task ):
		self.acquire()

		self.completedJobs += 1
		if elapsedTime > self.longestJobTime:
			self.longestJobTime = elapsedTime
			self.longestJobClass = str( task )

		self.release() 

	def getLongestJobTime( self ):
		return self.longestJobTime

	def getLongestJobClass( self ):
		return self.longestJobClass

	def getCompletedJobs( self ):
		return self.completedJobs

# ------------------------------------------------------------------------------
# Section: class Manager
# ------------------------------------------------------------------------------

# Not all processes(e.g. dbmgr) support isNextTickPending, so we default this 
# to False.
isNextTickPending = getattr( BigWorld, "isNextTickPending", lambda: False )

class Manager( object ):
	"""
	This class defines a background task manager that manages a pool
	of working threads. BackgroundTask objects are added to be processed by
	a background thread and then, possibly by the main thread again.
	"""

	def __init__( self, taskManagerName = "Unnamed",
			isNextTickPendingFn = lambda numProcessedTasks: isNextTickPending() ):
		"""
		Background Task Manager initialiser
		@param taskManagerName			The name of the task manager
		@param isNextTickPendingFn		This function is called when main thread
						tasks are executed, if it returns false more main thread
						tasks will be processed. Otherwise they will be processed
						during the next tick. numProcessedTasks is the number of
						jobs procesed this tick.
		"""
		self.numRunningThreads = 0
		self.__bgThreads = []
		# List of tasks to be performed in the background and foreground threads
		self.__bgTasks = Queue()
		self.__fgTasks = Queue()

		self._foregroundStats = Stats()
		self._backgroundStats = Stats( needsLock = True )

		self._isNextTickPendingFn = isNextTickPendingFn

		self.taskManagerName = taskManagerName
		self.addWatchers()

		self._readFD, self._writeFD = os.pipe()

		BigWorld.registerFileDescriptor( self._readFD,
			self.doMainThreadTasks, taskManagerName )
		BigWorld.addEventListener( "onFini", self.stopAll )

		self._writeLock = thread.allocate_lock()

		self.isDestroyed = False

		self.threshold = 0


	def __del__( self ):
		# Should already be stopped
		self.stopAll()


	def _destroy( self ):
		if not self.isDestroyed:
			self.isDestroyed = True
			self.removeWatchers()


	def doMainThreadTasks( self, fd = None ):
		"""
		This method processes queued main thread tasks.
		"""

		# Take off any data from the pipe as we're about to process
		os.read( self._readFD, 4096 )

		numProcessedTasks = 0
		hasFinishedQueue = False

		while not self._isNextTickPendingFn( numProcessedTasks ):

			try:
				fgTask = self.__fgTasks.get( False )
			except:
				hasFinishedQueue = True
				break

			try:
				startTime = time.time()

				fgTask.doMainThreadTask( self )

				elapsedTime = time.time() - startTime

				self._foregroundStats.onJobCompleted( elapsedTime, fgTask )
			except Exception, e:
				print e

			numProcessedTasks += 1

		if not hasFinishedQueue:
			print "Unable to process all main thread tasks, " \
				"{0} tasks still remaining".format( self.__fgTasks.qsize() )
			self.triggerMainThreadTasks()

	def addStatsWatcher( self, childPath, stats, queue ):
		BigWorld.addWatcher( "{path}/completedJobs".format( path = childPath ),
			stats.getCompletedJobs )
		BigWorld.addWatcher( "{path}/longestJobTime".format( path = childPath ),
			stats.getLongestJobTime )
		BigWorld.addWatcher( "{path}/longestJobClass".format( path = childPath ),
			stats.getLongestJobClass )
		BigWorld.addWatcher( "{path}/queueSize".format( path = childPath ), 
			queue.qsize )

	def addWatchers( self ):
		BigWorld.addWatcher( self.getWatcherPath( "numberOfThreads" ), 
			lambda: self.numRunningThreads )

		self.addStatsWatcher( self.getWatcherPath( "foreground" ),
				self._foregroundStats, self.__fgTasks )
		self.addStatsWatcher( self.getWatcherPath( "background" ),
				self._backgroundStats, self.__bgTasks )

	def getWatcherPath( self, *args ):
		return '/'.join( ("bgTaskManager", self.taskManagerName) + args )

	def removeWatchers( self ):
		BigWorld.delWatcher( self.getWatcherPath() )

	def onBgTaskJobComplete( self, elapsedTime, task ):
		self._backgroundStats.onJobCompleted( elapsedTime, task )

	def startThreads( self, numThreads, threadDataCreator = lambda : None,
				threadDataDestroyer = lambda data: None ):
		"""
		This method starts background worker threads. It should be called by
		the main thread.
		"""
		for i in range( 0, numThreads ):
			thread = _Thread( self, threadDataCreator, threadDataDestroyer )
			self.__bgThreads.append( thread )
			thread.start()

		self.numRunningThreads += numThreads


	def stopAll( self, isFinalStop = True ):
		"""
		This method stops background worker threads. It should be called by
		the main thread.
		"""
		if isFinalStop:
			self._destroy()

		for i in range( 0, self.numRunningThreads ):
			self.addBackgroundTask( None )


	def onThreadFinished( self, thread ):
		"""
		This method is called by the _ThreadFinisher to ensure the thread
		count of the manager is kept up to date on thread destruction.
		"""
		self.__bgThreads.remove( thread )
		self.numRunningThreads -= 1

		if self.isDestroyed and self.numRunningThreads == 0:
			BigWorld.deregisterFileDescriptor( self._readFD )

			os.close( self._readFD )
			os.close( self._writeFD )


	def addMainThreadTask( self, task ):
		"""This method adds a task back into the main thread for execution."""
		if not issubclass( task.__class__, BackgroundTask ):
			raise TypeError( "Main thread tasks must inherit from BackgroundTask" )

		self.__fgTasks.put( task )

		self.triggerMainThreadTasks()

	def triggerMainThreadTasks( self ):
		# Magic number '1' is just to send something over the pipe
		self._writeLock.acquire()
		try:
			os.write( self._writeFD, '1' )
		except OSError:
			# Due to the possibility of the ThreadFinisher tasks being processed
			# from a previous os.write, causing _writeFD to be closed.

			# TODO: It is possible for _writeFD to match a new FD, so this
			# should be resolved.
			pass
		self._writeLock.release()


	def addBackgroundTask( self, task ):
		"""This method adds a task into the background thread for execution."""
		if task and not issubclass( task.__class__, BackgroundTask ):
			raise TypeError( "Background tasks must inherit from BackgroundTask" )
		self.__bgTasks.put( task )


	def pullBackgroundTask( self ):
		"""
		This method removes and returns an item from the background task
		queue in a blocking manner.
		"""
		return self.__bgTasks.get( True )


	def setWarningThreshold( self, threshold ):
		self.threshold = max( threshold, 0 )

# ------------------------------------------------------------------------------
# Section: class BackgroundTask
# ------------------------------------------------------------------------------

class BackgroundTask( object ):
	"""
	This class provides the interface that should be inherited from and
	implemented by any code wishing to place a job in a BackgroundTask
	Manager.
	"""

	def doBackgroundTask( self, bgTaskMgr, threadData ):
		"""
		This method is called in a background thread to perform potentially
		thread blocking functionality.
		"""
		raise Exception( "Sub classes must implement this method" )


	def doMainThreadTask( self, bgTaskMgr ):
		"""
		This method is invoked in a foreground thread and can be used for
		invoking callbacks to code executing in the main Python thread.
		"""
		raise Exception( "Sub classes must implement this method" )


	def __str__( self ):
		"""
		This method should be overloaded in child classes.
		"""
		return "%s" % self.__class__.__name__

# ------------------------------------------------------------------------------
# Section: class _Thread
# ------------------------------------------------------------------------------

class _Thread( threading.Thread ):
	"""
	This class encapsulates a worker thread which is used for processing
	background queue tasks.
	"""

	def __init__( self, bgTaskMgr, dataCreator, dataDestroyer ):
		threading.Thread.__init__( self )
		self._bgTaskMgr = bgTaskMgr
		self._dataCreator = dataCreator
		self._dataDestroyer = dataDestroyer

	def join( self, timeout = None ):
		# Join should only occur during shut-down for Background task threads.
		# While this does not guarantee that this is the thread that stops
		# it does mean that if at least one thread stops, the shutdown loop
		# will keep doing this until all threads are joined. We do a
		# timeout join here to yield to the other threads.
		self._bgTaskMgr.addBackgroundTask( None )
		threading.Thread.join( self, 0.1 )

	def run( self ):
		"""
		This method continously pulls and executes background thread tasks.
		"""
		threadData = self._dataCreator()

		while True:
			bgTask = self._bgTaskMgr.pullBackgroundTask()

			if bgTask == None:
				break

			try:
				startTime = time.time()
				bgTask.doBackgroundTask( self._bgTaskMgr, threadData )
			except:
				threadName = threading.currentThread().getName()
				print "Caught exception in", threadName
				traceback.print_exc()

				# TODO: Should be a better way to do this. Deleting sys.exc_*
				# and sys.last_* did not work.
				# Generate a dummy exception to clear thread state so that the
				# bgTask will be deleted.
				try:
					raise Exception()
				except:
					pass

				print "Continuing thread", threadName
			finally:
				elapsedTime = time.time() - startTime
				threshold = self._bgTaskMgr.threshold 
				if threshold > 0 and elapsedTime > threshold:
					print "Last background task took {0} seconds and exceeded " \
						"threshold {1}. Task info: {2}".format(
							elapsedTime, threshold, str( bgTask ) )
				self._bgTaskMgr.onBgTaskJobComplete( elapsedTime, bgTask )

			# Do not keep a reference to the task while waiting for the next
			# one.
			del bgTask

		self._dataDestroyer( threadData )

		self._bgTaskMgr.addMainThreadTask( _ThreadFinisher( self ) )


# ------------------------------------------------------------------------------
# Section: class _ThreadFinisher
# ------------------------------------------------------------------------------

class _ThreadFinisher( BackgroundTask ):
	"""
	This class notifies the BackgroundTask.Manager that a thread has been
	destroyed.
	"""

	def __init__( self, thread ):
		BackgroundTask.__init__( self )
		self.thread = thread


	def doBackgroundTask( self, bgTaskMgr, threadData ):
		"""This method is not used. The class only works in the main thread"""
		raise Exception( "This method is not implemented" )


	def doMainThreadTask( self, bgTaskMgr ):
		"""This method notifies the BackgroundTask.Manager of thread death."""
		bgTaskMgr.onThreadFinished( self.thread )


# ------------------------------------------------------------------------------
# Section: Example BackgroundTasks
# ------------------------------------------------------------------------------

class _GILHoggingTask( BackgroundTask ):
	"""
	This class tests behaviour of monopolising the Python's Global Interpretor
	Lock. (ie: this is an example of what not to do)
	"""

	def __init__( self ):
		self.lower = 1
		self.upper = 9999999


	def doBackgroundTask( self, bgTaskMgr, threadData ):
		"""
		This method is an example of code not releasing the GIL.
		"""

		from random import randrange

		# Randomize a large list of integers
		# The GIL is released every N bytecodes
		numbers = range( self.lower, self.upper )
		for number in numbers:
			rnd = randrange( 0, len(numbers) - 1 )
			number, numbers[rnd] = numbers[rnd], number

		# Sorts the list
		# This actually calls a C function which does not release the GILL
		numbers.sort()

		bgTaskMgr.addMainThreadTask( self )


	def doMainThreadTask( self, bgTaskMgr ):
		print "GILHoggingTask done"

# BackgroundTask.py
