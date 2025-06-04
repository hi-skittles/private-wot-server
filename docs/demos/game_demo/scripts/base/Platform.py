import BigWorld

class Platform( BigWorld.Base ):

	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.createInDefaultSpace()
		print "Platform: created in default space"
		
	def onClientDeath( self ):
		self.destroyCellEntity()
		
	def onLoseCell( self ):
		self.destroy()
		
# Platfrom.py
		