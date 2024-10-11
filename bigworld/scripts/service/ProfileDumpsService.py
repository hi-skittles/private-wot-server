import re
import logging

import BigWorld
from TwistedWeb import TwistedWeb
from twisted.web.resource import Resource


from TWResources.file_resource import ( FileResource, FileRenderer,
		ProfileDumpsFileRenderer )
from service_utils import (ServiceConfig, ServiceConfigOption,
	ServiceConfigFileOption, ServiceConfigPortsOption)

log = logging.getLogger( __name__ )


class Config( ServiceConfig ):
	"""
	Configuration class for ProfileDumpsService.
	"""
	class Meta:
		SERVICE_NAME = "ProfileDumpsService"

	# Path to config file for self service, relative to the 'res' path.
	CONFIG_PATH = ServiceConfigFileOption(
		'server/config/services/profile_dumps.xml' )

	# Netmask used to select which network interface to listen on
	NETMASK = ServiceConfigOption( '', optionName = "interface" )
	
	DOCUMENT_ROOT = ServiceConfigOption( "",
						optionName = "profileDumpsDir" )


class ProfileDumpsService( TwistedWeb ):
	"""
	Generic HTTP L{Bigworld.Service} for serving files of Profile dumps.

	"""

	# Watchers used to advertise the address (ip and port) of this service
	PROFILE_DUMPS_ADDRESS = "services/data/profile_dumps_http"

	# List of regex patterns that this service will allow to be served.
	PATTERNS = (
		# Profile dump file name pattern
		r'_profile_\d{8}_\d{6}\.json$',
	)

	# List of regex objects thsat will be matched against file paths
	ACCESS_LIST = [ re.compile( p ) for p in PATTERNS ]


	def __init__( self ):
		TwistedWeb.__init__( self, netmask = Config.NETMASK )
	# __init__


	def createResources( self ):
		""" Implements superclass method TwistedWeb.createResources """

		root = Resource()
		root.putChild( "profiledumps", 
				FileResource( fileRendererCls = ProfileDumpsFileRenderer,
							whitelist = self.ACCESS_LIST,
							documentRoot = Config.DOCUMENT_ROOT ) )
		return root
	# createResources


	def initWatchers( self, interface ):
		""" Implements superclass method TwistedWeb.initWatchers """

		TwistedWeb.initWatchers( self, interface )

		# expose host:port
		BigWorld.addWatcher( self.PROFILE_DUMPS_ADDRESS,
						lambda: "%s:%d" % ( interface.host, interface.port ) )
	# initWatchers


	def finiWatchers( self ):
		""" Override from TwistedWeb. """
		BigWorld.delWatcher( self.PROFILE_DUMPS_ADDRESS )
		TwistedWeb.finiWatchers( self )

# end class ProfileDumpsService 


# ProfileDumpsService.py
