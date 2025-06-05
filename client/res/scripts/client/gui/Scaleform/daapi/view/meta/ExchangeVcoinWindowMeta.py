# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeVcoinWindowMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ExchangeVcoinWindowMeta(DAAPIModule):

    def buyVcoin(self):
        self._printOverrideError('buyVcoin')

    def as_setTargetCurrencyDataS(self, data):
        return self.flashObject.as_setTargetCurrencyData(data) if self._isDAAPIInited() else None

    def as_setSecondaryCurrencyS(self, value):
        return self.flashObject.as_setSecondaryCurrency(value) if self._isDAAPIInited() else None
