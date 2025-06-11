# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsControlMeta.py
# Compiled at: 2014-11-04 09:29:17
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsControlMeta(DAAPIModule):

    def showQuestsWindow(self):
        self._printOverrideError('showQuestsWindow')

    def as_isShowAlertIconS(self, value, highlight):
        return self.flashObject.as_isShowAlertIcon(value, highlight) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
