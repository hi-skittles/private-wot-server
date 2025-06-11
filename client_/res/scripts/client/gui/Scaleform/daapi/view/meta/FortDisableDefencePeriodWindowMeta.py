# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDisableDefencePeriodWindowMeta.py
# Compiled at: 2014-07-10 14:11:58
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortDisableDefencePeriodWindowMeta(DAAPIModule):

    def onClickApplyButton(self):
        self._printOverrideError('onClickApplyButton')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
