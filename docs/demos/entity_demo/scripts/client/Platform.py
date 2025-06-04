import BigWorld
import Keys

class Platform( BigWorld.Entity ):
	
	def onEnterWorld( self, prereqs ):
		
		#self.model = BigWorld.Model("sets/items/platform.model")
		self.model = BigWorld.PyModelObstacle( "sets/items/platform.model", self.matrix, True)
		self.model.vehicleID = self.id
		self.filter = BigWorld.PlayerAvatarFilter()
		
	def onLeaveWorld( self ):
		pass
		
	def enable( self ):
		self.physics = 0
		self.physics.userDirected = False
		self.physics.fall = False

	def kill( self ):
		self.cell.kill()
		
	def handleKeyEvent( self, event ):
		if not hasattr( self, "physics" ):
			return
		
		v = self.physics.velocity;
		speed = 15
		
		isDown = event.isKeyDown()
		
		# check for left and right movement
		if event.key == Keys.KEY_LEFTARROW:
			v.x = -speed * isDown
		elif event.key == Keys.KEY_RIGHTARROW:
			v.x = speed * isDown
			
		# check for updward and downward movement
		if event.key == Keys.KEY_PGUP:
			v.y = -speed * isDown
		elif event.key == Keys.KEY_PGDN:
			v.y = speed * isDown
			
		# check for backward and forward movement
		if event.key == Keys.KEY_DOWNARROW:
			v.z = -speed * isDown
		elif event.key == Keys.KEY_UPARROW:
			v.z = speed * isDown

		self.physics.velocity = v
		
		return False