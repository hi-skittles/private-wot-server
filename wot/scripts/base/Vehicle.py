import BigWorld

from bwdebug import DEBUG_MSG


class Vehicle(BigWorld.Proxy):
	def __init__(self):
		BigWorld.Base.__init__(self)
	
	def createCellNearHere(self, MAILBOX):
		DEBUG_MSG('createCellNearHere', MAILBOX)
	
	def onCreateCellSuccess(self):
		DEBUG_MSG('onCreateCellSuccess')
	
	def receiveFinalStats(self, PYTHON):
		DEBUG_MSG('receiveFinalStats', PYTHON)
	
	def setAvatar(self, MAILBOX):
		DEBUG_MSG('setAvatar', MAILBOX)
	
	def sendFinalStats(self, PYTHON):
		DEBUG_MSG('sendFinalStats', PYTHON)
	
	def smartDestroy(self):
		DEBUG_MSG('smartDestroy')
