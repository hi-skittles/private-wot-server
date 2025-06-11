import BigWorld
import Keys
import CommonDemo

class BaseAvatar( BigWorld.Entity ):
	
	def onEnterWorld( self, prereqs ):
	
		# create avatar model
		self.model = BigWorld.Model( *(CommonDemo.AVATAR_MODEL['files']) )
		self.filter = BigWorld.AvatarFilter()
		self.model.motors[0].matchCaps = CommonDemo.AVATAR_MODEL['matchCaps']
		
	def onLeaveWorld( self ):
		self.model = None
		
	def onPlayerEnterWorld( self, prereqs ):
		
		# set filter
		self.filter = BigWorld.PlayerAvatarFilter()
		
		# set physics
		self.physics = BigWorld.STANDARD_PHYSICS
		self.physics.velocityMouse = "Direction"
		self.physics.collide = True
		self.physics.fall = True
		self.physics.teleport( (0, 5, 0) )
		
		# set moving flags
		self.walking = False
		self.running = False
		self.moveForward = False
		self.moveBackward = False
		self.moveUpward = False
		self.moveLeft = False
		self.moveRight = False
		
	def handleKeyEvent( self, event ):
	
		# quick check to see if player has a physics object
		if not hasattr( self, "physics" ):
			return
			
		isDown = event.isKeyDown()
		
		# check speed modifiers
		if event.key == Keys.KEY_LSHIFT:
			self.walking = isDown
		elif event.key == Keys.KEY_LCONTROL:
			self.running = isDown
			
		# check for left and right movement
		if event.key == Keys.KEY_A:
			self.moveLeft = isDown
		elif event.key == Keys.KEY_D:
			self.moveRight = isDown
			
		# check for up movement
		if event.key == Keys.KEY_SPACE:
			self.moveUpward = isDown
			
		# check for backward and forward movement
		if event.key == Keys.KEY_S:
			self.moveBackward = isDown
		elif event.key == Keys.KEY_W:
			self.moveForward = isDown

		# update the velocity
		self.updateVelocity()
		
		# update platform
		if hasattr( self, "platform" ):
			self.platform.handleKeyEvent( event )
			
		return False
	
	# update the players velocity
	def updateVelocity( self ):

		speed = self.speed()
			
		xspeed = 0
		if self.moveLeft:
			xspeed = -speed
		elif self.moveRight:
			xspeed = speed
		
		yspeed = 0
		if self.moveUpward:
			yspeed = speed
	
		self.physics.fall = not self.moveUpward
			
		zspeed = 0
		if self.moveBackward:
			zspeed = -speed
		elif self.moveForward:
			zspeed = speed
		
		self.physics.velocity = ( xspeed, yspeed, zspeed )
		
	# get moving speed
	def speed( self ):
		if self.walking:
			return 1.5
		elif self.running:
			return 10
		else:
			return 5
		
# BaseAvatar.py
	