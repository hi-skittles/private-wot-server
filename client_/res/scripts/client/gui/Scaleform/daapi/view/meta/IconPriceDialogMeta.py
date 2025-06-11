# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IconPriceDialogMeta.py
# Compiled at: 2014-04-18 12:21:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class IconPriceDialogMeta(DAAPIModule):

    def as_setMessagePriceS(self, price, currency, actionPriceData):
        return self.flashObject.as_setMessagePrice(price, currency, actionPriceData) if self._isDAAPIInited() else None

    def as_setPriceLabelS(self, label):
        return self.flashObject.as_setPriceLabel(label) if self._isDAAPIInited() else None

    def as_setOperationAllowedS(self, isAllowed):
        return self.flashObject.as_setOperationAllowed(isAllowed) if self._isDAAPIInited() else None
