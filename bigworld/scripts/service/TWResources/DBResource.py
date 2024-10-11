import BigWorld

import BWTwoWay

import functools
from json_util import JSONResource, sendJSON, sendJSONError, returnJSONError
from twisted.web import resource, server

import BWTwoWay
import KeepAliveMailboxes

class LogOnResource( JSONResource ):
	def onResult( self, request, mailbox, dbID, wasActive ):
		if mailbox is None:
			sendJSONError( request,
					BWTwoWay.BWAuthenticateError( "No such user" ) )
			return

		KeepAliveMailboxes.add( mailbox.className, dbID, mailbox )

		# BigWorld.baseAppData[ ("Avatar", dbID) ] = mailbox
		sendJSON( request, { "id" : dbID, "type" : mailbox.className } )

	def onAuthenticateSuccess( self, request, result ):
		entityType, entityID = result
		BigWorld.createBaseAnywhereFromDBID( entityType, entityID,
				functools.partial( self.onResult, request ) )

	def onAuthenticateFailure( self, request, failure ):
		sendJSONError( request, failure.value )

	def render_GET( self, request ):
		print "logOn:", request.args
		try:
			deferred = BigWorld.authenticateAccount(
					request.args[ "username" ][0],
					request.args[ "password" ][0] )
		except KeyError, e:
			return returnJSONError( request, BWTwoWay.BWInvalidArgsError(
					"Argument %s not specified" % e ) )

		deferred.addCallbacks(
				functools.partial( self.onAuthenticateSuccess, request ),
				functools.partial( self.onAuthenticateFailure, request ) )

		return server.NOT_DONE_YET

class DBResource( JSONResource ):
	def __init__( self ):
		JSONResource.__init__( self )
		self.putChild( "logOn", LogOnResource() )

# DBResource.py
