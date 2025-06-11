# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/BaseContactViewMeta.py
# Compiled at: 2014-12-03 04:33:11
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BaseContactViewMeta(DAAPIModule):

    def onOk(self, data):
        self._printOverrideError('onOk')

    def onCancel(self):
        self._printOverrideError('onCancel')

    def as_updateS(self, data):
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None

    def as_setOkBtnEnabledS(self, isEnabled):
        return self.flashObject.as_setOkBtnEnabled(isEnabled) if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_closeViewS(self):
        return self.flashObject.as_closeView() if self._isDAAPIInited() else None
