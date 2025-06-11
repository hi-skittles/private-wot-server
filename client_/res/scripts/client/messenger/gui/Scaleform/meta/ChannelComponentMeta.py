# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ChannelComponentMeta.py
# Compiled at: 2014-12-22 07:19:07
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ChannelComponentMeta(DAAPIModule):

    def isJoined(self):
        self._printOverrideError('isJoined')

    def sendMessage(self, message):
        self._printOverrideError('sendMessage')

    def getHistory(self):
        self._printOverrideError('getHistory')

    def getMessageMaxLength(self):
        self._printOverrideError('getMessageMaxLength')

    def onLinkClick(self, linkCode):
        self._printOverrideError('onLinkClick')

    def as_setJoinedS(self, flag):
        return self.flashObject.as_setJoined(flag) if self._isDAAPIInited() else None

    def as_addMessageS(self, message):
        return self.flashObject.as_addMessage(message) if self._isDAAPIInited() else None
