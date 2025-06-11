# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/LobbyChannelWindowMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LobbyChannelWindowMeta(DAAPIModule):

    def as_getMembersDPS(self):
        return self.flashObject.as_getMembersDP() if self._isDAAPIInited() else None

    def as_hideMembersListS(self):
        return self.flashObject.as_hideMembersList() if self._isDAAPIInited() else None
