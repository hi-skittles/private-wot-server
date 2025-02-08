"""
The Account Client Entity script.

This entity is created when the client logs in.
"""
import BigWorld

# ------------------------------------------------------------------------------
# Section: class Account
# ------------------------------------------------------------------------------

class Account( BigWorld.Proxy ):
	def __init__( self ):
		BigWorld.Proxy.__init__( self )
		print "Client: Account.__init__"
		print self.__dict__
		print dir(self)

	def onFinish( self ):
		pass

	# Method is called if player has been kicked from the server.
	#	reason - reason why player has been kicked.
	#----------------------------------------------------------------------------------------------
	def onKickedFromServer( self, reason ):
		print 'onKickedFromServer: %s' % ( reason )


# Account.py