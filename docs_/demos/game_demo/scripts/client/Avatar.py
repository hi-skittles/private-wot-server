import BigWorld
import GUI
import Math
import Keys
import CommonDemo
from BaseAvatar import BaseAvatar

CAP = 1

class Avatar( BaseAvatar ):
		
	# avatar controls
	def onEnterWorld( self, prereqs ):
		BaseAvatar.onEnterWorld( self, prereqs )
		
		self.targetCaps = [CAP]
		
	def onLeaveWorld( self ):
		BaseAvatar.onLeaveWorld( self )
	
	def move( self, point, velocity = 1.0 ):
		self.cell.move( point, velocity )
	
	def stop( self ):
		self.cell.stop()
		
	def kill( self ):
		self.cell.kill()
		
	def platformEnabled( self ):
		self.platform.enable()
		
	def name( self ):
		return self.__class__.__name__
		
	def colour( self ):
		return (255, 0, 0)
		
class PlayerAvatar( Avatar ):

	def onEnterWorld( self, prereqs ):
		Avatar.onEnterWorld( self, prereqs )
		BaseAvatar.onPlayerEnterWorld( self, prereqs )
		
		# tracker
		self.headNodeInfo = BigWorld.TrackerNodeInfo(
				self.model,
				"biped Head",
				[ ( "biped Neck", -0.20 ),
				  ( "biped Spine", 0.50 ),
				  ( "biped Spine1", 0.40 ) ],
				"None",
				-60.0, 60.0,
				-80.0, 80.0,
				360.0 )	# 180
				
		self.tracker = BigWorld.Tracker()
		self.tracker.nodeInfo = self.headNodeInfo
		self.model.tracker = self.tracker
		self.entityDirProvider = BigWorld.EntityDirProvider(self, 1, 0)		
		self.tracker.directionProvider = self.entityDirProvider
		
		self.box = GUI.BoundingBox('')
		self.box.widthRelative = False
		self.box.heightRelative = False
		self.box.width = 32
		self.box.height = 32
		self.box.source = self.model.bounds
		self.box.absoluteSubspace = 2
		self.box.name = GUI.Text('')
		self.box.name.colour.green = 0
		self.box.name.colour.blue = 0
		self.box.name.verticalAnchor = "BOTTOM"
		self.box.name.position = (0.5, 1.0, 1.0)
		GUI.addRoot(self.box)
		
		moff = Math.Matrix()
		moff.setTranslate( Math.Vector3( 0.0, 1.5, 0.0 ) )
		mp = Math.MatrixProduct(); 
		mp.a = moff; 
		mp.b = self.matrix
		BigWorld.target.source = mp
		BigWorld.target.exclude = self
		BigWorld.target.selectionFovDegrees = 25.0
		BigWorld.target.deselectionFovDegrees = 80.0
		BigWorld.target.caps( 1, 2 )
		
		self.follow = False
		self.target = None
		
		CommonDemo.trace( "PlayerAvatar::onEnterWorld" )
		
	def onBecomePlayer( self ):
		CommonDemo.trace( "PlayerAvatar::onBecomePlayer" )
		
	def toggleTarget( self ):
		self.follow = not self.follow
		
		if self.follow and self.target:
			self.tracker.directionProvider = BigWorld.DiffDirProvider( self.matrix, self.target.matrix )
			CommonDemo.trace("toggle target look mode")
		else:
			self.tracker.directionProvider = self.entityDirProvider
			CommonDemo.trace("toggle target view mode")		

	# callback
	def targetFocus( self, entity ):
		self.target = entity
		self.box.source = entity.model.bounds
		self.box.name.text = entity.name()
		(r, g, b) = entity.colour()
		self.box.name.colour.red = r
		self.box.name.colour.green = g
		self.box.name.colour.blue = b
		
		if self.follow:
			self.tracker.directionProvider = BigWorld.DiffDirProvider( self.matrix, self.target.matrix )
		
	def targetBlur( self, entity ):
		self.target = None
		self.box.source = None
		self.box.name.text = ""
		
	def onLeaveWorld( self ):
		Avatar.onLeaveWorld( self )
		GUI.delRoot(self.box)
		self.box = None
		
		CommonDemo.trace("PlayerAvatar::onLeaveWorld")
		
	def handleKeyEvent( self, event ):
		BaseAvatar.handleKeyEvent( self, event )
		
	# player controls
	def capturePlatform( self, platform ):
		platform.cell.enableControl( self.id )
		self.platform = platform
		CommonDemo.trace( "Player has captured platform" )
		
	def releasePlatform( self ):
		if self.platform:
			self.platform.cell.disableControl()
			self.platform = None
			del self.platform
			CommonDemo.trace( "Player has released platform" )
		
	def spawn( self, type, position = None ):
		if position:
			self.cell.spawn( type, position )
		else:
			self.cell.spawn( type, self.position )
		CommonDemo.trace( "Player spawning", type )
		
	def spawnAll( self, type, count = 1, radius = 20.0 ):
		self.cell.spawnAll( type, count, radius )
		CommonDemo.trace( "Player spawning all" )
		
	def moveAll( self, radius = 20.0, velocity = 1.0 ):
		self.cell.moveAll( radius, velocity )
		CommonDemo.trace( "Player move all" )

	def stopAll( self ):
		self.cell.stopAll()
		CommonDemo.trace( "Player stop all" )
		
	def killAll( self ):
		self.cell.killAll()
		CommonDemo.trace( "Player kill all" )
	
# Avatar.py
	