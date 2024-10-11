import BigWorld
import functools

from twisted.web import resource, server

from json_util import JSONResource

from CallMailboxResource \
	 import makeCallEntityResourceByName, makeCallEntityResourceByID, \
	 		makeCallMailboxResource

import KeepAliveMailboxes

# This method is used to intercept a call to
# entities_by_id/Account/<id>/webChooseCharacter.
#
# This is needed so that the new mailbox can be cached locally and so that an
# appropriate result can be returned. (i.e. not the mailbox but a description of
# it).
def cacheCharacterMailbox( response ):
	mailbox, dbID = response
	KeepAliveMailboxes.add( mailbox.className, dbID, mailbox )

	return { "type" : mailbox.className, "id" : dbID }

filters = {
	("Account", "webChooseCharacter"): cacheCharacterMailbox
}


def makeCallEntityResource( entitiyType, entityID, methodName ):
	mailbox = KeepAliveMailboxes.get( entitiyType, entityID )

	filter = filters.get( (entitiyType, methodName) )

	if mailbox:
		return makeCallMailboxResource( mailbox, methodName, filter )
	else:
		return makeCallEntityResourceByID( entitiyType, entityID, methodName,
				addToKeepAliveCache = True,
				filterFn = filter )

class PathAccumulatorResource( JSONResource ):
	def __init__( self, depth, constructor ):
		JSONResource.__init__( self )
		self.depth = depth
		self.constructor = constructor
		self.args = []

	def getChild( self, name, request ):
		self.args.append( name )

		if len( self.args ) == self.depth:
			return self.constructor( *self.args )
		else:
			return self

class DeepResource( JSONResource ):
	def __init__( self, depth, constructor ):
		JSONResource.__init__( self )
		self.depth = depth
		self.constructor = constructor

	def getChild( self, name, request ):
		resource = PathAccumulatorResource( self.depth, self.constructor )
		return resource.getChild( name, request )

def EntitiesByNameResource():
	return DeepResource( 3, makeCallEntityResourceByName )

def EntitiesByIDResource():
	return DeepResource( 3, makeCallEntityResource )

# EntitiesResource.py
