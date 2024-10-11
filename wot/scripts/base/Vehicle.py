import BigWorld

class Vehicle(BigWorld.Proxy):
    def __init__(self):
        BigWorld.Base.__init__(self)

    def createCellNearHere(self, MAILBOX):
        pass

    def onCreateCellSuccess(self):
        pass

    def receiveFinalStats(self, PYTHON):
        pass

    def setAvatar(self, MAILBOX):
        pass

    def sendFinalStats(self, PYTHON):
        pass

    def smartDestroy(self):
        pass
