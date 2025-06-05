# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileWindowMeta.py
# Compiled at: 2013-10-21 08:32:28
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileWindowMeta(DAAPIModule):

    def userAddFriend(self):
        self._printOverrideError('userAddFriend')

    def userSetIgnored(self):
        self._printOverrideError('userSetIgnored')

    def userCreatePrivateChannel(self):
        self._printOverrideError('userCreatePrivateChannel')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_updateS(self, data):
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None

    def as_addFriendAvailableS(self, value):
        return self.flashObject.as_addFriendAvailable(value) if self._isDAAPIInited() else None

    def as_setIgnoredAvailableS(self, value):
        return self.flashObject.as_setIgnoredAvailable(value) if self._isDAAPIInited() else None

    def as_setCreateChannelAvailableS(self, value):
        return self.flashObject.as_setCreateChannelAvailable(value) if self._isDAAPIInited() else None
