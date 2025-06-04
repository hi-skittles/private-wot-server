import BigWorld

class Space( BigWorld.Base ):

	def __init__( self ):
		BigWorld.Base.__init__( self )

		# Create this entity in a new space
		self.createInNewSpace()
		self.cell.addGeometryMapping( self.spaceDir )

		self.registerGlobally( "DefaultSpace", self.onRegistered )

	def onRegistered( self, succeeded ):
		if not succeeded:
			print "Failed to register space."
			self.destroyCellEntity()

	def onGetCell( self ):
		print "Space.onGetCell loading entities from '%s'" % \
			self.spaceDir
		BigWorld.fetchEntitiesFromChunks( self.spaceDir,
				EntityLoader( self ) )

	def onLoseCell( self ):

		# Once our cell entity is destroyed, it's safe to clean up the Proxy.
		# We can't just call self.destroy() in onClientDeath() above, as
		# destroyCellEntity() is asynchronous and the cell entity would still
		# exist at that point.
		self.destroy()


class EntityLoader:
	def __init__( self, spaceEntity ):
		self.spaceEntity = spaceEntity

	def onSection( self, entity, matrix ):
		entityType = entity.readString( "type" )
		properties = entity[ "properties" ]
		pos = matrix.applyToOrigin()

		# Create entity base
		BigWorld.createBaseAnywhere( entityType,
			properties,
			createOnCell = self.spaceEntity.cell,
			position = pos,
			direction = (matrix.roll, matrix.pitch, matrix.yaw) )

	def onFinish( self ):
		print "Finished loading entities for space", \
			self.spaceEntity.spaceDir

# Space.py
