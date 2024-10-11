import ResMgr
import BigWorld
from TwistedWeb import TwistedWeb

from TWResources.json_util import JSONResource
from TWResources.DBResource import DBResource
from TWResources.GlobalEntitiesResource import GlobalEntitiesResource
from TWResources.EntitiesResource import (EntitiesByNameResource,
	EntitiesByIDResource)

from service_utils import (ServiceConfig, ServiceConfigOption,
	ServiceConfigFileOption, ServiceConfigPortsOption)


class Config( ServiceConfig ):
	"""
	Configuration class for HTTPGameService.
	"""

	class Meta:
		SERVICE_NAME = 'HTTPGameService'
		READ_ONLY_OPTIONS = ["PORTS"]

	# Path to config file for self service, relative to the 'res' path.
	CONFIG_PATH = ServiceConfigFileOption(
		'server/config/services/http_game.xml' )

	# List of ports to try to bind to.
	PORTS = ServiceConfigPortsOption( [0] )

	# Netmask used to select which network interface to listen on
	NETMASK = ServiceConfigOption( '', optionName = "interface" )


class HTTPGameService( TwistedWeb ):
	"""
	Performs remote execution of entity methods over HTTP.
	"""

	def __init__( self ):
		TwistedWeb.__init__( self, portOrPorts = Config.PORTS,
			netmask = Config.NETMASK )
	# __init__


	def createResources( self ):
		""" Implements superclass method TwistedWeb.createResources """

		root = JSONResource()

		root.putChild( "entities_by_name", EntitiesByNameResource() )
		root.putChild( "entities_by_id", EntitiesByIDResource() )
		root.putChild( "global_entities", GlobalEntitiesResource() )
		root.putChild( "db", DBResource() )

		return root
	# createResources


# end class HTTPResTreeService


# HTTPGameService.py
