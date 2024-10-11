import BigWorld

from bwdebug import DEBUG_MSG


class Login(BigWorld.Base):
    def __init__(self):
        BigWorld.Base.__init__(self)

    def onEnqueued(self, STRING, UINT64):
        DEBUG_MSG('onEnqueued', STRING, UINT64)
        pass

    def onQueueTurn(self):
        DEBUG_MSG('onQueueTurn')
        pass

    def onAccountClientReleased(self, MAILBOX):
        DEBUG_MSG('onAccountClientReleased', MAILBOX)
        pass
