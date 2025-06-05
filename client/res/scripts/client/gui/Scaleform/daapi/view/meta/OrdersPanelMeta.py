# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/OrdersPanelMeta.py
# Compiled at: 2014-12-20 15:28:33
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class OrdersPanelMeta(DAAPIModule):

    def getOrderTooltipBody(self, orderID):
        self._printOverrideError('getOrderTooltipBody')

    def as_setPanelPropsS(self, data):
        return self.flashObject.as_setPanelProps(data) if self._isDAAPIInited() else None

    def as_setOrdersS(self, orders):
        return self.flashObject.as_setOrders(orders) if self._isDAAPIInited() else None

    def as_updateOrderS(self, data):
        return self.flashObject.as_updateOrder(data) if self._isDAAPIInited() else None
