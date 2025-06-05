# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EliteWindowMeta.py
# Compiled at: 2013-10-28 08:33:21
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class EliteWindowMeta(DAAPIModule):

    def as_setVehicleS(self, vehicle):
        return self.flashObject.as_setVehicle(vehicle) if self._isDAAPIInited() else None
