"""
This file contains framework classes for BigWorld automated tests
"""

import os
import sys
import unittest

import inspect
import types

from bwtest import config
from bwtest import log
from primitives import locallog

from util import strclass

import inspect
import time

class TestCase( unittest.TestCase ):
	"""Base class for all user defined test cases.
	Test developers should sub-class this class and provide
	setUp and runTest methods. setUp needs a call to addCleanup"""
	
	def __init__( self ):
		"""Constructor.  Sub-class should not overload this.
		Rather do initialization in the setUp method
		"""
		self.context = {}
		self.type = None

		self.setUpWrapped = self.setUp
		self.setUp = self.setUpWrapper

		self.tearDownWrapped = self.tearDown
		self.tearDown = self.tearDownWrapper

		unittest.TestCase.__init__( self, '_runBWTest' )
		
		if not hasattr( self, "name" ):
			self.name = self.__class__.__name__

		if not hasattr( self, "description" ):
			if self.__doc__:
				self.description = self.__doc__
			else:
				self.description = ""


	def setUpWrapper( self ):
		"""
		This method wraps setUp() with a call to tearDown() on exception to ensure
		we are always cleaned up.
		"""

		log.progress( "Test case: %s", self.name )
		if not config.DRY_RUN:
			self.currentResult = None
			self.startup_time = time.time()

			try:
				self.setUpWrapped()
			except:
				self.tearDownWrapper()
				raise


	def tearDownWrapper( self ):
		"""
		This method wraps tearDown() with user added clean up methods.
		"""
		if not config.DRY_RUN:
			try:
				self.tearDownWrapped()
			finally:
				if config.SERVER_LOG_DIR is not None:
					self._archive_logs()


	def _runBWTest( self ):
		steps = self._collectSteps()
		for stepItem in steps:
			log.progress( "Step: " + stepItem[ 'desc' ] )

			step = stepItem[ 'step' ]
			if not config.DRY_RUN:
				step()


	def produceStats( self ):
		""" Returns JSON object containing meta-data for this test case """

		steps = self._collectSteps()

		return {
			'name': self.name,
			'description': self.description,
			'tags': self.tags,
			'steps': steps
		}


	def _collectSteps( self ):
		""" Discovers and returns steps in this TestCase"""

		methods = inspect.getmembers( self, inspect.ismethod )
		stepsDict = {}
		steps = []
		runTestAdded = False
		for method in methods:
			if method[0].startswith( 'step' ):
				stepsDict[ method[0] ] = method[1]
			if method[0] == 'runTest':
				stepsDict[ method[0] ] = method[1]
				runTestAdded = True

		if len( stepsDict ) > 1 and runTestAdded:
			raise Exception( "conflict: %s:%s: both runTest and steps exist!" %\
				(self.__module__, self.name) )

		for stepName in sorted( stepsDict ):
			step = stepsDict[ stepName ]
			steps.append( { 'step': step, 
							'desc': formatDocLines( step.__doc__ ) } )

		return steps

	def _archive_logs( self ):
		"""
		Search and archive server logs for each test case from setUp to tearDown.
		"""
		fileName = config.SERVER_LOG_DIR + '/' + self.__module__ + "." +\
			self.__class__.__name__ + '.log'

		if self._resultForDoCleanups.failures or \
			self._resultForDoCleanups.errors:
			delta = int( time.time() - self.startup_time + 1 )
			logs = locallog.grepLastServerLog( None, lastSeconds = delta )
			logFile = open( fileName, 'w' )
			logFile.write( logs )
			logFile.close()
		elif os.path.exists( fileName ):
			os.remove( fileName )



class TestSuite( unittest.TestSuite ):
	"""Class for grouping related test cases together. Can be instantiated but
	creating a folder with __init__.py to create a module will organise all 
	TestCase in that folder in to one suite.
	"""
	
	
	def __init__( self, name, description, tags, priority = None ):
		"""Constructor. Can set these params in __init__.py 
		of your module if using that approach
		@param name: Name of the suite
		@param description: Description of the suite
		@param tags: List of user-defined tags. These are your filter for
					 ./runtests -t
		@param priority: Set this value to control the order that different
						 suites are run
		"""
		unittest.TestSuite.__init__( self, [] )

		self.name = name
		self.description = description
		self.tags = tags
		self.testcases = []
		self.testsuites = []
		if priority != None:		
			self.priority = priority


	def __repr__(self):
		return "<%s tests=%s, suites=%s>" % (strclass(self.__class__), self.testcases, self.testsuites)


	def produceStats( self ):
		""" Returns JSON object containing meta-data for this test suite."""

		ret = { 
			'name': self.name,
			'description': self.description,
			'tags': self.tags,
			'testcases': []
		}

		# loop through testcases and run produceStats on it
		for testcase in self.testcases:
			ret['testcases'].append( testcase.props.produceStats() )

		return ret


	def addSuites( self, suites ):
		"""Add sub-suites.
		@param suites: List of suites to add"""
		self.testsuites.extend( suites )


	def addCases( self, cases ):
		"""Add testcases.
		@param cases: List of testcases to add"""
		self.testcases.extend( cases )


	def run( self, result ):
		"""Executes all tests in the suite. Should not need to call this.
		@param result: Container for results of the test cases.
		"""
		
		log.progress( "Test suite: %s", self.name )
		case = None
		try:
			for case in self.testcases:
				case.run( result )
		except KeyboardInterrupt:
			log.error("ctrl-c caught. Wait for cleanups to be done")
			if case:
				case.tearDownWrapper()
			raise
		for suite in self.testsuites:
			suite.run( result )
		
# ----

def formatDocLines( doctext ):
	"""Formats python doc string for output to console.
	@param doctext: Python doc string taken from __doc__
	"""
	if doctext is None:
		return "<no description>"
	lines = doctext.strip( ' \n\t' ).split( '\n' )
	lines = [ line.strip(' \n\t' ) for line in lines ]
	res = ' '.join( lines )
	return res


def addParameterizedTestCases( parent, parameters ):
	""" Generates a set of TestCase class definitions based on a parent class
		and provided list of parameter dictionaries
		@param parent: Super class definition
		@param parameters: List of parameter dictionaries
							eg. [{"key1": 1, "key2": 2}, {"key1": 3, "key2": 4}]
	"""
	
	for caseParams in parameters:
		testClassDict = {}
		testClassDict["name"] = parent.name
		testClassDict["description"] = parent.description
		testClassName = parent.__name__
		testClassDict["description"] += " Parameters:" 
		for key, value in caseParams.items():
			testClassDict["name"] += " %s %s" % (key, value)
			testClassDict["description"] += " %s = %s" % (key, value)
			testClassDict[key] = value
			testClassName += "%s%s" % (key, value)
		#Create sub-class of parent and TestCase with one set of parameters
		classDef = type( testClassName, ( parent, TestCase ), testClassDict )
		classDef.__module__ = parent.__module__
		
		module = inspect.getmodule( parent )
		module.__dict__[testClassName] = classDef

		
def addCombinedTestCases( parent, parameters):
	"""Generates a test case for each combination of parameters provided in a
	dictionary of lists 
	@param parent: Super class definition
	@param parameters: List of parameter dictionaries
					   eg. {"key1": [1, 2], "key2": [3, 4]}
	"""
	parameterList = []
	for key, values in parameters.items():
		if not values:
			raise Exception( "Can't do combinations with an empty list" )
		if parameterList:
			newParameterList = []
			for x in parameterList:
				for y in values:
					temp = x.copy()
					temp.update({key: y})
					newParameterList.append( temp )
			parameterList = newParameterList
		else:
			parameterList = [{key: x} for x in values]
	addParameterizedTestCases( parent, parameterList )

		

