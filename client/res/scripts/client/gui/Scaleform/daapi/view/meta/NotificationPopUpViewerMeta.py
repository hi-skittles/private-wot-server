# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationPopUpViewerMeta.py
# Compiled at: 2015-01-22 11:22:13
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class NotificationPopUpViewerMeta(DAAPIModule):

    def setListClear(self):
        self._printOverrideError('setListClear')

    def onMessageHided(self, byTimeout, wasNotified):
        self._printOverrideError('onMessageHided')

    def onClickAction(self, typeID, entityID, action):
        self._printOverrideError('onClickAction')

    def getMessageActualTime(self, msTime):
        self._printOverrideError('getMessageActualTime')

    def as_getPopUpIndexS(self, typeID, entityID):
        return self.flashObject.as_getPopUpIndex(typeID, entityID) if self._isDAAPIInited() else None

    def as_appendMessageS(self, messageData):
        return self.flashObject.as_appendMessage(messageData) if self._isDAAPIInited() else None

    def as_updateMessageS(self, messageData):
        return self.flashObject.as_updateMessage(messageData) if self._isDAAPIInited() else None

    def as_removeMessageS(self, typeID, entityID):
        return self.flashObject.as_removeMessage(typeID, entityID) if self._isDAAPIInited() else None

    def as_removeAllMessagesS(self):
        return self.flashObject.as_removeAllMessages() if self._isDAAPIInited() else None

    def as_layoutInfoS(self, data):
        return self.flashObject.as_layoutInfo(data) if self._isDAAPIInited() else None

    def as_initInfoS(self, maxMessagessCount, padding):
        return self.flashObject.as_initInfo(maxMessagessCount, padding) if self._isDAAPIInited() else None
