# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderSelectPopoverMeta.py
# Compiled at: 2015-01-10 10:21:05
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortOrderSelectPopoverMeta(DAAPIModule):

    def addOrder(self, orderID):
        self._printOverrideError('addOrder')

    def removeOrder(self, orderID):
        self._printOverrideError('removeOrder')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
