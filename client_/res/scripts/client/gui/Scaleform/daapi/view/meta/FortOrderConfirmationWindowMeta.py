# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderConfirmationWindowMeta.py
# Compiled at: 2014-02-24 12:45:11
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortOrderConfirmationWindowMeta(DAAPIModule):

    def submit(self, count):
        self._printOverrideError('submit')

    def getTimeStr(self, time):
        self._printOverrideError('getTimeStr')

    def as_setDataS(self, value):
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None

    def as_setSettingsS(self, value):
        return self.flashObject.as_setSettings(value) if self._isDAAPIInited() else None
