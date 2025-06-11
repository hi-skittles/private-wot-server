# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReceivedInviteWindowMeta.py
# Compiled at: 2013-08-08 11:35:55
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ReceivedInviteWindowMeta(DAAPIModule):

    def acceptInvite(self):
        self._printOverrideError('acceptInvite')

    def declineInvite(self):
        self._printOverrideError('declineInvite')

    def cancelInvite(self):
        self._printOverrideError('cancelInvite')

    def as_setTitleS(self, value):
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setReceivedInviteInfoS(self, value):
        return self.flashObject.as_setReceivedInviteInfo(value) if self._isDAAPIInited() else None
