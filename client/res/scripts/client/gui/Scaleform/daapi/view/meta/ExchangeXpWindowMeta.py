# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeXpWindowMeta.py
# Compiled at: 2013-10-01 07:59:31
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ExchangeXpWindowMeta(DAAPIModule):

    def as_vehiclesDataChangedS(self, isHaveElite, data):
        return self.flashObject.as_vehiclesDataChanged(isHaveElite, data) if self._isDAAPIInited() else None

    def as_totalExperienceChangedS(self, value):
        return self.flashObject.as_totalExperienceChanged(value) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None
