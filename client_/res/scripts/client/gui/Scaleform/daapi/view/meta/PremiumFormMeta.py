# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PremiumFormMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class PremiumFormMeta(DAAPIModule):

    def onPremiumBuy(self, days, price):
        self._printOverrideError('onPremiumBuy')

    def onPremiumDataRequest(self):
        self._printOverrideError('onPremiumDataRequest')

    def as_setCostsS(self, costs):
        return self.flashObject.as_setCosts(costs) if self._isDAAPIInited() else None

    def as_setGoldS(self, gold):
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_setPremiumS(self, isPremium):
        return self.flashObject.as_setPremium(isPremium) if self._isDAAPIInited() else None
