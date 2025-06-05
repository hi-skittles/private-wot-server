# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PrbSendInvitesWindowMeta.py
# Compiled at: 2015-01-16 11:10:19
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class PrbSendInvitesWindowMeta(DAAPIModule):

    def showError(self, value):
        self._printOverrideError('showError')

    def setOnlineFlag(self, value):
        self._printOverrideError('setOnlineFlag')

    def sendInvites(self, accountsToInvite, comment):
        self._printOverrideError('sendInvites')

    def getAllAvailableContacts(self):
        self._printOverrideError('getAllAvailableContacts')

    def as_onReceiveSendInvitesCooldownS(self, value):
        return self.flashObject.as_onReceiveSendInvitesCooldown(value) if self._isDAAPIInited() else None

    def as_setDefaultOnlineFlagS(self, onlineFlag):
        return self.flashObject.as_setDefaultOnlineFlag(onlineFlag) if self._isDAAPIInited() else None

    def as_showClanOnlyS(self, showClanOnly):
        return self.flashObject.as_showClanOnly(showClanOnly) if self._isDAAPIInited() else None

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_onContactUpdatedS(self, contact):
        return self.flashObject.as_onContactUpdated(contact) if self._isDAAPIInited() else None

    def as_onListStateChangedS(self, isEmpty):
        return self.flashObject.as_onListStateChanged(isEmpty) if self._isDAAPIInited() else None
