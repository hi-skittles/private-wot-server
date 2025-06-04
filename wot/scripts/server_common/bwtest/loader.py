"""
Module used to traverse through a directory structure and find test cases
"""

import os
import sys
import inspect
import pkgutil

from bwtest import TestCase, TestSuite, log
from functools import partial

def transformLegacySteps( testCase ):
	"""
	Transform deprecated stepXXX() into testXXX()

	@param testCase: The test case to transform
	"""

	steps = [(name, method)
			for name, method in inspect.getmembers( testCase, inspect.ismethod )
			if name.startswith( 'step' ) ]

	if not steps:
		return testCase

	sortKey = lambda step: int( step[0].replace( "step", "" ) )
	steps = sorted( steps, key = sortKey )

	log.warning( "transformLegacySteps: %s has deprecated stepXXX()" % testCase )

	def combiner( self, steps ):
		for step in steps(): step[1]()

	testMethod = partial( combiner, testCase, steps )

	name = "test%s" % testCase.__class__.__name__.replace( "Test", "" )
	setattr( testCase, name, testMethod )

	return testCase


def filter( includeTags, excludedTags, names, testCase ):
	"""
	Checks if a TestCase has test method, tags and name filters

	@param includeTags:		TestCase tags not matching are filterd out
	@param excludedTags:	TestCase tags matching tags are filterd out
	@param names:			TestCase name not matching are filtered out
	@param testCase:		TestCase going through the filter
	"""

	klass = testCase.__class__

	if hasattr( klass, "tags" ):
		tags = set( klass.tags )
	else:
		tags = set()

	if includeTags and not tags.intersection( includeTags ):
		return False

	if excludedTags and tags.intersection( excludedTags ):
		return False

	if names and klass.__name__ not in names:
		return False

	for methodName in dir( testCase ):
		if (methodName.startswith( 'test' ) or methodName == "runTest") and	\
			callable( getattr( testCase, methodName ) ):
			return True

	return False


def parseDir( dir, filter ):
	"""
	Recursively parse directory into TestSuites

	@param dir:		Root directory to recursively discover test cases
	@param filter:	Method to test if a discovered test case is filtered out
	"""

	dir = dir.rstrip( "/" )
	name = dir.split( "/" )[-1]
	prefix = dir.replace( os.path.sep, '.' ) + "."
	suite = TestSuite( name, "", [ "ALL" ], None )
	
	for fileName in os.listdir( dir ):
		
		subDir = os.path.join( dir, fileName )
		if os.path.isdir( subDir ):
			subSuite = parseDir( subDir, filter )
			if subSuite.testsuites or subSuite.testcases:
				suite.testsuites.append( subSuite )
			continue

		if not fileName.endswith( ".py" ):
			continue

		moduleName = prefix + fileName.split( "." )[0]
		__import__( moduleName )
		module = sys.modules[ moduleName ]
		
		for klassName, klass in inspect.getmembers( module, inspect.isclass ):
			if not issubclass( klass, TestCase ):
				continue

			testCase = klass()
			testCase = transformLegacySteps( testCase )

			if filter( testCase ):
				suite.testcases.append( testCase )

	return suite


def discover( dir, includeTags, excludedTags, names ):
	"""
	Loads top level TestSuite

	@param dir:				Root directory to recursively discover test cases
	@param includeTags:		TestCases not matching are filterd out
	@param excludedTags:	TestCases matching tags are filterd out
	@param names:			TestCases not matching are filtered out
	"""

	f = partial( filter, includeTags, excludedTags, names )
	return parseDir( dir, f )
