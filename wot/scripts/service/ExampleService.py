import BigWorld
from service_utils import ServiceConfig


class Config( ServiceConfig ):
	"""
	This class will set up the watchers for the example config values.
	"""
	class Meta:
		SERVICE_NAME = 'ExampleService'

	OPTION_1 = 400
	OPTION_2 = 'test'


class ExampleService( BigWorld.Service ):
	"""
	Example service.
	"""
	def myTest( self, arg ):
		print( "myTest: {} ({}, {})".format( arg, Config.OPTION_1,
			Config.OPTION_2 ) )

	def twoWay( self, arg1, arg2, arg3, arg4 ):
		print "twoWay:", arg1, arg2, arg3, arg4
		result = [s.upper() for s in (arg1, arg2, arg3, arg4)]
		return tuple( result )


# ExampleService.py
