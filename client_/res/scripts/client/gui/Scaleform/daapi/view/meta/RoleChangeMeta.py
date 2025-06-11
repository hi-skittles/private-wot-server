# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RoleChangeMeta.py
# Compiled at: 2014-12-22 09:35:20
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class RoleChangeMeta(DAAPIModule):

    def onVehicleSelected(self, vehicleId):
        self._printOverrideError('onVehicleSelected')

    def changeRole(self, role, vehicleId):
        self._printOverrideError('changeRole')

    def as_setCommonDataS(self, data):
        return self.flashObject.as_setCommonData(data) if self._isDAAPIInited() else None

    def as_setRolesS(self, roles):
        return self.flashObject.as_setRoles(roles) if self._isDAAPIInited() else None

    def as_setPriceS(self, priceString, enoughGold):
        return self.flashObject.as_setPrice(priceString, enoughGold) if self._isDAAPIInited() else None
