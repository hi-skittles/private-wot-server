# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationsListMeta.py
# Compiled at: 2015-01-22 11:22:13
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class NotificationsListMeta(DAAPIModule):

    def onClickAction(self, typeID, entityID, action):
        self._printOverrideError('onClickAction')

    def getMessageActualTime(self, msTime):
        self._printOverrideError('getMessageActualTime')

    def as_setInitDataS(self, value):
        return self.flashObject.as_setInitData(value) if self._isDAAPIInited() else None

    def as_setMessagesListS(self, value):
        return self.flashObject.as_setMessagesList(value) if self._isDAAPIInited() else None

    def as_appendMessageS(self, messageData):
        return self.flashObject.as_appendMessage(messageData) if self._isDAAPIInited() else None

    def as_updateMessageS(self, messageData):
        return self.flashObject.as_updateMessage(messageData) if self._isDAAPIInited() else None
