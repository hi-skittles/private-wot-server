# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleBuyWindowMeta.py
# Compiled at: 2014-10-20 10:37:38
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class VehicleBuyWindowMeta(DAAPIModule):

    def submit(self, data):
        self._printOverrideError('submit')

    def storeSettings(self, expanded):
        self._printOverrideError('storeSettings')

    def as_setGoldS(self, gold):
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_setCreditsS(self, value):
        return self.flashObject.as_setCredits(value) if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setEnabledSubmitBtnS(self, enabled):
        return self.flashObject.as_setEnabledSubmitBtn(enabled) if self._isDAAPIInited() else None
