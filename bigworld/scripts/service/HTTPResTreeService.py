import re
import logging

import ResMgr
import BigWorld
from TwistedWeb import TwistedWeb
from twisted.web.resource import Resource

from TWResources.file_resource import ResFileRenderer, FileResource

from service_utils import (ServiceConfig, ServiceConfigOption,
	ServiceConfigFileOption)

log = logging.getLogger( __name__ )


class Config( ServiceConfig ):
	"""
	Configuration class for HTTPResTreeService.
	"""
	class Meta:
		SERVICE_NAME = "HTTPResTreeService"

	# Path to config file for self service, relative to the 'res' path.
	CONFIG_PATH = ServiceConfigFileOption(
		'server/config/services/http_res_tree.xml' )

	# Netmask used to select which network interface to listen on
	NETMASK = ServiceConfigOption( '', optionName = "interface" )


class HTTPResTreeService( TwistedWeb ):
	"""
	Generic HTTP L{Bigworld.Service} for serving files from the 'res' tree
	subject to simple pattern-based whitelisting.

	See also L{ResTreeResource}.
	"""

	# Watchers used to advertise the IP of this service
	SERVICE_ADDRESS = "services/HTTPResTreeService/address"
	SPACEVIEWER_ADDRESS = "services/data/space_viewer_http"

	# List of regex patterns that this service will allow to be served.
	PATTERNS = (

		# spaceviewer entity icons
		r'/space_viewer_images/\w+\.png$',

		# parent dir of spaceviewer background tiles
		r'/space_viewer/'
	)

	# List of regex objects thsat will be matched against file paths
	ACCESS_LIST = [ re.compile( p ) for p in PATTERNS ]


	def __init__( self ):
		TwistedWeb.__init__( self, netmask = Config.NETMASK )
	# __init__


	def createResources( self ):
		""" Implements superclass method TwistedWeb.createResources """

		root = Resource()
		root.putChild( "res", FileResource( fileRendererCls = ResFileRenderer,
											whitelist = self.ACCESS_LIST,
											documentRoot = None ) )
		return root
	# createResources


	def initWatchers( self, interface ):
		""" Implements superclass method TwistedWeb.initWatchers """

		TwistedWeb.initWatchers( self, interface )

		# expose host:port
		BigWorld.addWatcher(
			self.SPACEVIEWER_ADDRESS,
			lambda: "%s:%d" % ( interface.host, interface.port ) )
	# initWatchers


	def finiWatchers( self ):
		""" Override from TwistedWeb. """
		BigWorld.delWatcher( self.SPACEVIEWER_ADDRESS )
		TwistedWeb.finiWatchers( self )
	# finiWatchers


# end class HTTPResTreeService


# HTTPResTreeService.py
