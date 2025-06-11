# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TankCarouselMeta.py
# Compiled at: 2014-09-17 12:34:03
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TankCarouselMeta(DAAPIModule):

    def vehicleChange(self, vehicleInventoryId):
        self._printOverrideError('vehicleChange')

    def buySlot(self):
        self._printOverrideError('buySlot')

    def buyTankClick(self):
        self._printOverrideError('buyTankClick')

    def setVehiclesFilter(self, nation, tankType, ready):
        self._printOverrideError('setVehiclesFilter')

    def getVehicleTypeProvider(self):
        self._printOverrideError('getVehicleTypeProvider')

    def as_setCarouselFilterS(self, filter):
        return self.flashObject.as_setCarouselFilter(filter) if self._isDAAPIInited() else None

    def as_setParamsS(self, params):
        return self.flashObject.as_setParams(params) if self._isDAAPIInited() else None

    def as_updateVehiclesS(self, vehiclesData, isSet):
        return self.flashObject.as_updateVehicles(vehiclesData, isSet) if self._isDAAPIInited() else None

    def as_showVehiclesS(self, compactDescrList):
        return self.flashObject.as_showVehicles(compactDescrList) if self._isDAAPIInited() else None
