# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MessengerBarMeta.py
# Compiled at: 2014-05-24 06:53:35
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class MessengerBarMeta(DAAPIModule):

    def channelButtonClick(self):
        self._printOverrideError('channelButtonClick')

    def contactsButtonClick(self):
        self._printOverrideError('contactsButtonClick')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None
