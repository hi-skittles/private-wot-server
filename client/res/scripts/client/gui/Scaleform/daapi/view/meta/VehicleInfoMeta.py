# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleInfoMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class VehicleInfoMeta(DAAPIModule):

    def getVehicleInfo(self):
        self._printOverrideError('getVehicleInfo')

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def as_setVehicleInfoS(self, vehicleInfo):
        return self.flashObject.as_setVehicleInfo(vehicleInfo) if self._isDAAPIInited() else None
