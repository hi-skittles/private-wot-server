# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeWindowMeta.py
# Compiled at: 2013-10-01 07:59:31
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ExchangeWindowMeta(DAAPIModule):

    def as_setSecondaryCurrencyS(self, credits):
        return self.flashObject.as_setSecondaryCurrency(credits) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None
