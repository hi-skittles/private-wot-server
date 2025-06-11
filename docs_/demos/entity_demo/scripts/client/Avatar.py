import BigWorld
import Keys
import CommonDemo
import TrainingDemo
from BaseAvatar import BaseAvatar

class Avatar( BaseAvatar ):
		
	# avatar controls
	def onEnterWorld( self, prereqs ):
		BaseAvatar.onEnterWorld( self, prereqs )
		
		self.filter = TrainingDemo.getFilter()
		
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
		
class PlayerAvatar( Avatar ):

	def onEnterWorld( self, prereqs ):
		Avatar.onEnterWorld( self, prereqs )
		BaseAvatar.onPlayerEnterWorld( self, prereqs )
		CommonDemo.trace( "PlayerAvatar::onEnterWorld" )
		
	def onBecomePlayer( self ):
		CommonDemo.trace( "PlayerAvatar::onBecomePlayer" )		
		
	def onLeaveWorld( self ):
		Avatar.onLeaveWorld( self )
		CommonDemo.trace( "PlayerAvatar::onLeaveWorld" )
		
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
		
	def spawnAll( self, type, count = 10, radius = 30.0 ):
		self.cell.spawnAll( type, count, float( radius ) )
		CommonDemo.trace( "Player spawning all" )
		
	def moveAll( self, radius = 20.0, velocity = 5.0 ):
		self.cell.moveAll( float( radius ), float( velocity ) )
		CommonDemo.trace( "Player move all" )

	def stopAll( self ):
		self.cell.stopAll()
		CommonDemo.trace( "Player stop all" )
		
	def killAll( self ):
		self.cell.killAll()
		CommonDemo.trace( "Player kill all" )
	
# Avatar.py
	
