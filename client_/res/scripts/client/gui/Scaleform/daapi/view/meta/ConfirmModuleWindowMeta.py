# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ConfirmModuleWindowMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ConfirmModuleWindowMeta(DAAPIModule):

    def submit(self, count, currency):
        self._printOverrideError('submit')

    def as_setDataS(self, value):
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None

    def as_setSettingsS(self, value):
        return self.flashObject.as_setSettings(value) if self._isDAAPIInited() else None
