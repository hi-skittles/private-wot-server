import BigWorld
import Keys
import CommonDemo
from BaseAvatar import BaseAvatar

class Avatar( BaseAvatar ):
		
	# avatar controls
	def onEnterWorld( self, prereqs ):
		BaseAvatar.onEnterWorld( self, prereqs )
		
	def onLeaveWorld( self ):
		BaseAvatar.onLeaveWorld( self )
		
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
	
# Avatar.py
	