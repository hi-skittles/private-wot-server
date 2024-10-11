import BigWorld


from CallMailboxResource import makeCallMailboxResource
from twisted.web import resource
from json_util import JSONResource, NoSuchEntityErrorPage

class GlobalEntitiesResource( JSONResource ):
	def getChild( self, name, request ):
		return GlobalEntityResource( name )

class GlobalEntityResource( JSONResource ):
	def __init__( self, globalName ):
		JSONResource.__init__( self )
		self.globalName = globalName

	def getChild( self, name, request ):
		try:
			mailbox = BigWorld.globalBases[ self.globalName ]
		except KeyError:
			return NoSuchEntityErrorPage( self.globalName )

		return makeCallMailboxResource( mailbox, name )

# GlobalEntitiesResource.py
