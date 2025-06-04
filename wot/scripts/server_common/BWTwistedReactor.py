"""
Twisted reactor for BigWorld
"""

import sys

from zope.interface import implements

from twisted.internet.interfaces import IReactorFDSet
from twisted.internet import posixbase
from twisted.python import log

import BigWorld

import functools
import time

import threading

from twisted.internet import defer

frequentTasksRunning = False

STARTUP_TIMEOUT = 10.0
SHUTDOWN_TIMEOUT = 10.0

FREQUENT_TASK_PERIOD = 0.1


# This class is used to 'tick' the reactor during startup and shutdown, when
# FrequentTasks are not being ticked.
class FrequentTaskThread(threading.Thread):
	def __init__(self, tickFunc, shouldStopFunc, onStopFunc, timeout):
		threading.Thread.__init__(self)
		self.onStopFunc = onStopFunc
		self.tickFunc = tickFunc
		self.shouldStopFunc = shouldStopFunc
		self.timeout = timeout
	
	def run(self):
		timeoutTime = time.time() + self.timeout
		
		while not self.shouldStopFunc():
			if time.time() > timeoutTime:
				print "Error: BWTwistedReactor FrequentTaskThread timed out"
				self.onStopFunc()
				return
			
			self.tickFunc()
			time.sleep(FREQUENT_TASK_PERIOD)
		
		self.onStopFunc()


class BigWorldReactor(posixbase.PosixReactorBase):
	"""
	A select() based reactor - runs on all POSIX platforms and on Win32.

	@ivar _reads: A dictionary mapping L{FileDescriptor} instances to arbitrary
		values (this is essentially a set).  Keys in this dictionary will be
		checked for read events.

	@ivar _writes: A dictionary mapping L{FileDescriptor} instances to
		arbitrary values (this is essentially a set).  Keys in this dictionary
		will be checked for writability.
	"""
	implements(IReactorFDSet)
	
	def __init__(self):
		"""
		Initialize file descriptor tracking dictionaries and the base class.
		"""
		self._reads = {}
		self._writes = {}
		self.isFrequentTask = False
		posixbase.PosixReactorBase.__init__(self)
	
	seconds = time.time
	
	def startRunning(self, installSignalHandlers=True):
		posixbase.PosixReactorBase.startRunning(self, installSignalHandlers)
		if not self.isFrequentTask:
			BigWorld.addFrequentTask(self.onFrequentTask)
			self.isFrequentTask = True
		
		# Need to tick reactor until frequent tasks actually start
		self.startFrequentTaskThread(self.shouldStopStartupThread,
		                             lambda: None,
		                             STARTUP_TIMEOUT)
		BigWorld.addEventListener("onFini", self.onFini)
	
	def shouldStopStartupThread(self):
		return frequentTasksRunning
	
	def shouldStopShutdownThread(self):
		return not self.running
	
	def startFrequentTaskThread(self, shouldStopFunc, onStopFunc, timeout):
		# Need to start a thread to tick the reactor (during onInit and onFini)
		# as frequent tasks may not be running
		t = FrequentTaskThread(self.runUntilCurrent, shouldStopFunc,
		                       onStopFunc, timeout)
		t.start()
	
	def onFini(self):
		print "BigWorldReactor.onFini: Stopping reactor"
		if self.running:
			self.stop()
			
			# The reactor can take some time to shut down. This includes
			# shutting down reactor threads.
			# Need to defer the actual finish. If not done, deadlock occurs.
			deferred = defer.Deferred()
			onStopFunc = lambda: deferred.callback(None)
			self.startFrequentTaskThread(self.shouldStopShutdownThread,
			                             onStopFunc, SHUTDOWN_TIMEOUT)
			
			return deferred
	
	def doBigWorldIteration(self, timeout):
		print "doBigWorldIteration"
	
	def onFrequentTask(self):
		# Used to stop the startup thread
		global frequentTasksRunning
		frequentTasksRunning = True
		
		self.runUntilCurrent()
	
	doIteration = doBigWorldIteration
	
	def doRead(self, reader, fd):
		why = reader.doRead()
		
		if why:
			self._disconnectSelectable(reader, why, True)
	
	def addReader(self, reader):
		"""
		Add a FileDescriptor for notification of data available to read.
		"""
		self._reads[reader] = 1
		BigWorld.registerFileDescriptor(reader,
		                                functools.partial(self.doRead, reader))
	
	def doWrite(self, reader, fd):
		why = reader.doWrite()
		
		if why:
			self._disconnectSelectable(reader, why, False)
	
	def addWriter(self, writer):
		"""
		Add a FileDescriptor for notification of data available to write.
		"""
		if not self._writes.has_key(writer):
			self._writes[writer] = 1
			BigWorld.registerWriteFileDescriptor(writer,
			                                     functools.partial(self.doWrite, writer))
	
	def removeReader(self, reader):
		"""
		Remove a Selectable for notification of data available to read.
		"""
		if reader in self._reads:
			del self._reads[reader]
			BigWorld.deregisterFileDescriptor(reader)
	
	def removeWriter(self, writer):
		"""
		Remove a Selectable for notification of data available to write.
		"""
		if writer in self._writes:
			del self._writes[writer]
			BigWorld.deregisterWriteFileDescriptor(writer)
	
	def removeAll(self):
		return self._removeAll(self._reads, self._writes)
	
	def getReaders(self):
		return self._reads.keys()
	
	def getWriters(self):
		return self._writes.keys()


from twisted.internet.main import installReactor

alreadyInstalled = False


def install():
	"""Configure the twisted mainloop to be run using the select() reactor.
	"""
	global alreadyInstalled
	if alreadyInstalled:
		return
	alreadyInstalled = True
	
	installReactor(BigWorldReactor())


__all__ = ['install']
