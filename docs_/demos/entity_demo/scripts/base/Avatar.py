import BigWorld

class Avatar( BigWorld.Proxy ):

	def __init__( self ):
		BigWorld.Proxy.__init__( self )
		self.createCellEntity( BigWorld.globalBases[ "DefaultSpace" ].cell )
		print "Avatar: created in default space"
		
	def onClientDeath( self ):
		self.destroyCellEntity()
		
	def onLoseCell( self ):
		self.destroy()
		
# Avatar.py
		