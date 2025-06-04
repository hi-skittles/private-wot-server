import BigWorld
import Math
import math

CURSOR_CAMERA = 0
REVERSE_CAMERA = 1
FREE_CAMERA = 2

class Camera:
	
	def __init__( self ):
	
		# initialise cursor camera
		self.cursorCamera = BigWorld.CursorCamera()
		self.cursorCamera.source = BigWorld.dcursor().matrix
		self.cursorCamera.target = BigWorld.PlayerMatrix()
		self.cursorCamera.pivotPosition = (0.0, 1.8, 0.0)
		self.cursorDistance = self.cursorCamera.pivotMaxDist
		
		# initialise free camera
		self.freeCamera = BigWorld.FreeCamera()
		
		# set camera type
		self.currentCamera = CURSOR_CAMERA		
	
	def handleMouseEvent( self, event ):
		if event.dz != 0:
			# change pivot distance base on mouse wheel
			clicks = event.dz / 120.0 # each wheel displacment is 120
			nextDist = self.cursorDistance - clicks
			
			if nextDist < 0:
				nextDist = 0
			elif nextDist > 10:
				nextDist = 10
				
			self.updatePivotDistance( nextDist )
			
		return self.cursorCamera.handleMouseEvent( event )
					
	def updatePivotDistance( self, distance ):
		camera = self.cursorCamera
		camera.firstPerson = distance == 0
		camera.pivotMaxDist = distance
		camera.maxDistHalfLife = 0.15
		self.cursorDistance = distance
		
	def setCamera( self, type ):
		self.currentCamera = type
		if self.currentCamera == CURSOR_CAMERA:
			BigWorld.camera( self.cursorCamera )
			self.cursorCamera.reverseView = False
		elif self.currentCamera == REVERSE_CAMERA:
			BigWorld.camera( self.cursorCamera )
			self.cursorCamera.reverseView = True
		else:
			BigWorld.camera( self.freeCamera )
			matrix = Math.Matrix()
			matrix.setIdentity()
			(x, y, z) = BigWorld.player().position
			matrix.setTranslate( (x, y + 2, z - 2 ) )
			matrix.invert()
			BigWorld.camera().set(matrix)
			
	def increaseFov( self ):
		fov = BigWorld.projection().fov + 0.1
		if fov < math.pi:
			BigWorld.projection().fov = fov
		
	def decreaseFov( self ):
		fov = BigWorld.projection().fov - 0.1
		if fov > 0:
			BigWorld.projection().fov = fov
			
# Camera.py