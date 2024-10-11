"""
This module is imported by the BigWorld engine before BWAutoImport, and handles
connecting wrappers for deprecated methods and types to their new names.

It is also the canonical record of the BigWorld Python API deprecation schedule.

It should be safe to backport newer versions into older releases.
"""
import functools
import sys
import warnings

def deprecatedAlias( method, oldname ):
	"""
	Decorator function, enclosing module, oldname, newname and warnings.
	"""
	def warnAndCallWrapper( *args, **kwargs ):
		"""
		Wrapper around method to raise a DeprecationWarning
		and call through to method
		"""
		warnings.warn( "%s.%s is deprecated, use %s.%s instead" % (
				method.__module__, oldname, method.__module__, method.__name__ ),
			DeprecationWarning, 2 )
		return method( *args, **kwargs )
	return functools.wraps( method )( warnAndCallWrapper )


def addDeprecatedAliasOf( module, newname, oldname ):
	"""
	Add oldname as a deprecated alias of newname in __module__
	"""
	if not hasattr( module, newname ):
		# New method does not exist
		return
	if hasattr( module, oldname ):
		# Deprecated alias already exists
		return
	method = getattr( module, newname )
	setattr( module, oldname, deprecatedAlias( method, oldname ))


import BigWorld
#### Deprecated as of BigWorld 1.8:
if BigWorld.component == "client":
	addDeprecatedAliasOf( BigWorld, "serverTime", "stime" )

#### Deprecated as of BigWorld 2.4:
addDeprecatedAliasOf( BigWorld, "ThirdPersonTargetingMatrix", "ThirdPersonTargettingMatrix" )
addDeprecatedAliasOf( BigWorld, "MouseTargetingMatrix", "MouseTargettingMatrix" )

#### Deprecated as of BigWorld 2.5:
if BigWorld.component == "client":
	if not hasattr( BigWorld, "cachedEntities" ):
		BigWorld.cachedEntities = {}
	if not hasattr( BigWorld, "allEntities" ):
		BigWorld.allEntities = BigWorld.entities

#### Deprecated as of BigWorld 2.6:
