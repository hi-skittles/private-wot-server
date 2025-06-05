# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortSettingsPeripheryPopoverMeta.py
# Compiled at: 2014-06-26 04:49:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortSettingsPeripheryPopoverMeta(DAAPIModule):

    def onApply(self, server):
        self._printOverrideError('onApply')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTextsS(self, data):
        return self.flashObject.as_setTexts(data) if self._isDAAPIInited() else None
