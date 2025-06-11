import BigWorld

class Platform( BigWorld.Entity ):
	
	def enableControl( self, sourceId, playerId ):
		entity = BigWorld.entities[playerId]
		self.controlledBy = entity.base
		entity.ownClient.platformEnabled()
		print "Platform: enable control"
		
	def disableControl( self, sourceId ):
		self.controlledBy = None
		print "Platform: disable control"
		
	def kill( self, sourceId ):
		self.destroy()
		print "Platform: killed"
		
# Platform.py
	