"""
This is a glue module that help server apps communicate with bwtest framework
"""

# import sys
# import os

# sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../../../..' )

# from bwtest.bwharness import TestCase
# from unittest import TestSuite, TestResult

import watcher
import common_snippets
from snippet_decorator import testSnippet, testStep

from watcher import assertTrue, assertFalse, assertEqual, assertNotEqual, \
					finish, mark 

