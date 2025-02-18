import BigWorld


class Space(BigWorld.Entity):
	
	def __init__(self, nearbyEntity):
		BigWorld.Entity.__init__(self)
		
		# This is the first entity created for the space
		assert (nearbyEntity is None)
	
	def onDestroy(self):
		# Destroy the space and all entities in it
		self.destroySpace()
	
	def addGeometryMapping(self, geometryToMap):
		# The base informs us which geometry to map.
		BigWorld.addSpaceGeometryMapping(self.spaceID, None, geometryToMap)

# Space.py
