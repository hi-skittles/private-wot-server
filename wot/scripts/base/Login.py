import BigWorld

from bwdebug import DEBUG_MSG, TRACE_MSG


TRACE_MSG('Login.py')

class Login(BigWorld.Proxy):
    def __init__(self):
        BigWorld.Proxy.__init__(self)
        self.loginPriority = len([accounts for accounts in BigWorld.entities.values() if type(accounts) == Login])
        TRACE_MSG('Login::init %s' % self.__dict__)
        self.onEnqueued(self.accountDBID_s, self.loginPriority)
    
    
    def onClientDeath(self):
        DEBUG_MSG('Login::onClientDeath : %d' % self.id)
        self.destroy()
    
    def onGiveClientToFailure(self):
        DEBUG_MSG('Login::onGiveClientToFailure')
    
    def onLogOnAttempt(self, ip, port, password):
        TRACE_MSG('Login::onLogOnAttempt  ', ip, port, password)
        return BigWorld.LOG_ON_REJECT

    def onEnqueued(self, STRING, UINT64):
        DEBUG_MSG('Login::onEnqueued', STRING, UINT64)
        BigWorld.addTimer(self.onQueueTurn, 0, 5, 0)
        
    def callback1(self, baseRef, databaseID, wasActive):
        DEBUG_MSG('Login::callback1', baseRef, databaseID, wasActive)
        if baseRef:
            DEBUG_MSG('Login::callback1: baseRef true')
            self.onAccountClientReleased(baseRef)
        else:
            DEBUG_MSG('Login::callback1: baseRef false')
            self.onAccountClientReleased(BigWorld.createEntity('Account', {'normalizedName': self.accountDBID_s}))

    def onQueueTurn(self, id, userArg):
        self.ownClient.receiveLoginQueueNumber(self.loginPriority)
        DEBUG_MSG('Login::onQueueTurn', self.loginPriority)
        if getattr(self, 'loginPriority', None) is None:
            DEBUG_MSG('Login::onQueueTurn: no loginPriority')
            BigWorld.delTimer(id)
            self.onClientDeath()
        elif self.loginPriority == 0:
            DEBUG_MSG('Login::onQueueTurn: loginPriority == 0')
            BigWorld.delTimer(id)
            self.ownClient.receiveLoginQueueNumber(self.loginPriority)
            BigWorld.createBaseAnywhereFromDB('Account', self.accountDBID_s, self.callback1)
        else:
            self.loginPriority -= 1
            self.ownClient.receiveLoginQueueNumber(self.loginPriority)

    def onAccountClientReleased(self, MAILBOX):
        DEBUG_MSG('Login::onAccountClientReleased', MAILBOX)
        self.giveClientTo(MAILBOX)
        self.destroy()
