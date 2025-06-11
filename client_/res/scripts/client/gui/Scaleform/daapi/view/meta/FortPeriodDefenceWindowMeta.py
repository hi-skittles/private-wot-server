# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortPeriodDefenceWindowMeta.py
# Compiled at: 2015-01-09 11:17:48
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortPeriodDefenceWindowMeta(DAAPIModule):

    def onApply(self, data):
        self._printOverrideError('onApply')

    def onCancel(self):
        self._printOverrideError('onCancel')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTextDataS(self, data):
        return self.flashObject.as_setTextData(data) if self._isDAAPIInited() else None
