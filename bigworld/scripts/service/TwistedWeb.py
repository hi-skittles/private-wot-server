
import logging

import BigWorld
import service_utils

import BWTwistedReactor
BWTwistedReactor.install()

import collections
import json

from twisted.web.server import Site
from twisted.internet import reactor
from twisted.internet.error import CannotListenError

log = logging.getLogger( __name__ )

ANY_PORT = 0
ALL_INTERFACES = '0.0.0.0'


class TwistedWeb( BigWorld.Service ):
	"""
	Base class for services that run over HTTP.
	"""

	def __init__( self, portOrPorts=ANY_PORT, netmask=None ):
		"""
		Constructor.

		@param portOrPorts 	Either a single port number, or a sequence of port
							numbers to try to bind to. If no ports are
							available, twisted.internet.error.CannotListenError
							is raised.
		@param netmask 		The interface to bind to.
		"""

		# BigWorld.getNetworkInterfaces() requires '' to mean "no netmask"
		if not netmask:
			netmask = ''

		host = self.getNetworkInterface( netmask )
		if not host:
			raise OSError(
				"No network interfaces available (netmask=%s)" % netmask )

		BigWorld.Service.__init__( self )

		rootResource = self.createResources()

		site = Site( rootResource )

		interface = self.startRunning( site, host, portOrPorts )

		self.initWatchers( interface )

	# __init__


	def createResources( self ):
		"""
		Creates a tree of twisted L{Resource} nodes that will be walked
		during the URL path resolution phase of a service (HTTP) request.

		Returns the root L{Resource}.
		"""
		log.warning( "No Resources configured for class %s",
			self.__class__.__name__ )

	# createResources


	def initWatchers( self, interface ):
		"""
		This method initialises the watchers.

		@param interface 	The interface and port this instance has bound to.
		"""

		service_utils.addStandardWatchers( self.__class__ )

		# expose host, port as a watcher
		BigWorld.addWatcher(
			"services/" + self.__class__.__name__ + "/address",
			lambda: "%s:%d" % ( interface.host, interface.port )
		)
	# initWatchers


	def finiWatchers( self ):
		"""
		This method finalises the watchers.

		Subclasses that override this method should call this method after
		removing watchers added in initWatchers to remove the service-level
		path.
		"""

		BigWorld.delWatcher(
			"services/" + self.__class__.__name__ + "/address" )

		BigWorld.delWatcher( "services/" + self.__class__.__name__ )

	# finiWatchers


	def startRunning( self, site, host=ALL_INTERFACES, portOrPorts=ANY_PORT ):
		"""
		Begins serving the given twisted L{Site} on the given host and port.

		@param site 			The Site to serve.
		@param host 			The interface to serve on.
		@param portOrPorts 		Either a single port, or a sequence of ports to
								attempt binding on.
		@return 				The interface that was bound.
		"""

		ports = portOrPorts
		if not isinstance( portOrPorts, collections.Sequence ):
			ports = [portOrPorts]

		port = None
		self.listeningPort = None
		for port in ports:
			try:
				self.listeningPort = reactor.listenTCP( port, site,
					interface=host )
				break
			except CannotListenError:
				pass

		if not self.listeningPort:
			raise CannotListenError( host, port,
				"All ports tried = %r" % (portOrPorts,) )

		interface = self.listeningPort.getHost()

		log.info(
			"%s( %d ): Bound to %s:%d",
			self.__class__.__name__, self.id, interface.host, interface.port
		)

		if not reactor.running:
			reactor.startRunning()
			# Initialize the thread pool to avoid lazy init.
			reactor.getThreadPool()

		return interface

	# startRunning


	def onDestroy( self ):
		"""
		Callback when this service is destroyed.
		"""
		log.info( "%s.onDestroy", self.__class__.__name__ )

		self.finiWatchers()

		if self.listeningPort:
			deferredDisconnect = self.listeningPort.stopListening()
			deferredDisconnect.addCallback( self.onDisconnect )
	# onDestroy


	def onDisconnect( self ):
		log.debug( "TwistedWeb.onDisconnect: connection closed" )
		self.listeningPort = None
	# onDisconnect


	def getNetworkInterface( self, netmask='' ):
		"""
		Returns the IP of the network interface to which this service should
		bind.

		Default implementation returns the first interface that matches the
		given netmask when a netmask is given, otherwise this method returns
		the BigWorld internal interface as given by BigWorld.address().
		"""

		if not netmask:
			host = BigWorld.address()[ 0 ]
			log.info( "%s( %d ): Using default internal interface %s",
				self.__class__.__name__, self.id, host )
			return host

		interfaces = BigWorld.getNetworkInterfaces( netmask )

		if not interfaces:
			raise service_utils.InvalidServiceConfiguration(
				"No network interfaces match the given netmask '%s': %r",
				netmask, BigWorld.getNetworkInterfaces() )

		# arbitrarily use first matching
		host = interfaces[ 0 ][ 0 ]
		log.info( "%s( %d ): Using network interface %s (netmask=%s)",
			self.__class__.__name__, self.id, host, netmask )
		return host

	# getNetworkInterface

# end class TwistedWeb


# TwistedWeb.py
