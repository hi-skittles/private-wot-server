import BigWorld
import Keys
import CommonDemo
from BaseAvatar import BaseAvatar

from functools import partial

AVATAR_MODEL = 0
STRIFF_MODEL = 1
SPIDER_MODEL = 2
ORC_MODEL = 3

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
				
		self.gunAimingNodeInfo = BigWorld.TrackerNodeInfo(
				self.model,
				"biped Spine",
				[	( "biped Spine1", 1 ),
					( "biped Neck", 1 ) ],
				"biped Spine",
				-60.0, 60.0,
				-80.0, 80.0,
				270.0 )
				
		self.handNodeInfo = BigWorld.TrackerNodeInfo(
				self.model,
				"biped Spine",
				[	( "biped R Hand", 1 ),
					( "biped R Forearm", 1 ),
					( "biped R UpperArm", 1 ) ],
				"None",
				-60.0, 60.0,
				-80.0, 80.0,
				270.0 )
				
		self.tracker = BigWorld.Tracker()
		self.tracker.nodeInfo = self.headNodeInfo
		self.model.tracker = self.tracker
		self.entityDirProvider = BigWorld.EntityDirProvider(self, 1, 0)		
		self.tracker.directionProvider = self.entityDirProvider
		
		self.currentModelIdx = 0
		
		CommonDemo.trace( "PlayerAvatar::onEnterWorld" )
		
	def onBecomePlayer( self ):
		CommonDemo.trace( "PlayerAvatar::onBecomePlayer" )
		
	def onLeaveWorld( self ):
		Avatar.onLeaveWorld( self )
		CommonDemo.trace( "PlayerAvatar::onLeaveWorld" )
		
	def handleKeyEvent( self, event ):
		BaseAvatar.handleKeyEvent( self, event )
		
	def toggleModel( self ):
		self.currentModelIdx = (self.currentModelIdx + 1) % len( CommonDemo.ALL_MODELS )
		modelInfo = CommonDemo.ALL_MODELS[ self.currentModelIdx ]

		self.model = BigWorld.Model( *modelInfo['files'] )
		self.model.motors[0].matchCaps = modelInfo['matchCaps']
		
		
	def toggleBackgroundModel( self ):
		self.currentModelIdx = (self.currentModelIdx + 1) % len( CommonDemo.ALL_MODELS )
		modelInfo = CommonDemo.ALL_MODELS [ self.currentModelIdx ]

		loadedCB = partial( self.onLoaded, modelInfo )
		BigWorld.loadResourceListBG( modelInfo['files'], loadedCB )

		
	def onLoaded( self, modelInfo, resourceRefs ):
		self.model = BigWorld.Model( *modelInfo['files'] )
		self.model.motors[0].matchCaps = modelInfo['matchCaps']
		
	
# Avatar.py
