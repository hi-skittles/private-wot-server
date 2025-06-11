# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseExchangeWindowMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BaseExchangeWindowMeta(DAAPIModule):

    def exchange(self, data):
        self._printOverrideError('exchange')

    def as_setPrimaryCurrencyS(self, value):
        return self.flashObject.as_setPrimaryCurrency(value) if self._isDAAPIInited() else None

    def as_exchangeRateS(self, value, actionValue):
        return self.flashObject.as_exchangeRate(value, actionValue) if self._isDAAPIInited() else None
