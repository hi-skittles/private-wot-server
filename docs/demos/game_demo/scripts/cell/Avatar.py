import BigWorld
import random
import math

MOVE_TIME = 5

class Avatar( BigWorld.Entity ):
	
	def __init__( self ):
		self.moveId = 0
		self.timerId = 0
		self.movementCentre = ( 0.0, 0.0, 0.0 )
		self.moveRadius = 0.0
		self.moveVelocity = 0.0

	
	def move( self, sourceId, point, velocity ):
		self.moveId = self.moveToPoint( point, velocity )
		print "Avatar: Told by", sourceId, "to move to", point, "with speed", velocity


	# Finishing callback for moveToPoint
	def onMove( self, controllerID, userData ):
		self.moveId = 0


	# Error callback for moveToPoint
	def onMoveFailure( self, controllerID, userData ):
		print "Movement failed for Avatar", self.id


	def stop( self, sourceId ):
		self.cancel( self.moveId )
		self.moveId = 0
		self.cancel( self.timerId )
		self.timerId = 0
		print "Avatar:", sourceId, "stopped"
		
		
	def kill( self, sourceId ):
		self.destroy()
		print "Avatar:", sourceId, "killed"	


	def randomPosition( self, centrePos, radius ):
		angle = random.uniform( -math.pi, math.pi )
		x = math.cos( angle )
		z = math.sin( angle )
		p = centrePos
		r = random.uniform( 0, radius )
		return (p.x + x * r, p.y, p.z + z * r )


	def onTimer( self, controllerID, userData ):
		destinationPoint = self.randomPosition( self.movementCentre, self.moveRadius )
		self.move( self.id, destinationPoint, self.moveVelocity )
		self.timerId = self.addTimer( MOVE_TIME , 0 )


	# Create a new Cell only entity
	def spawn( self, sourceId, type, position ):
		newPosition = (position[0], position[1] + 1, position[2] )
		e = BigWorld.createEntity( type, self.spaceID, newPosition, (0, 0, 0) , {} )
		print "Avatar:", sourceId, "spawned entity", e.id, "at", newPosition

	
	def spawnAll( self, sourceId, type, count, radius ):
		caller = BigWorld.entities[ sourceId ]
		for i in range( 0, count ):
			self.spawn( sourceId, type, self.randomPosition( caller.position, radius ) )


	# This method is invoked to move all the surrounding entities
	def moveAll( self, sourceId, radius, velocity ):
		for e in BigWorld.entities.values():
			if e.id != sourceId and isinstance(e, Avatar):
				e.setMovement( sourceId, radius, velocity )


	def setMovement( self, sourceId, moveRadius, moveVelocity ):
		if (self.timerId != 0):
			print "Avatar: Warning, movement timer already exists"

		caller = BigWorld.entities[ sourceId ]
		self.movementCentre = caller.position
		self.moveRadius = moveRadius
		self.moveVelocity = moveVelocity

		destinationPoint = self.randomPosition( self.movementCentre, moveRadius )
		self.move( sourceId, destinationPoint, moveVelocity )
		self.timerId = self.addTimer( MOVE_TIME, 0 )


	def stopAll( self, sourceId ):
		for e in BigWorld.entities.values():
			if e.id != sourceId and isinstance(e, Avatar):
				e.stop( e.id )


	def killAll( self, sourceId ):
		for e in BigWorld.entities.values():
			if e.id != sourceId:
				e.kill( e.id )

# Avatar.py
			
