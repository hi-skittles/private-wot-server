"""Generic utility methods
"""

def strclass(cls):
	"""Represent a class type as a string
	@param cls: Class type to represent.
	"""
	return "%s.%s" % (cls.__module__, cls.__name__)

