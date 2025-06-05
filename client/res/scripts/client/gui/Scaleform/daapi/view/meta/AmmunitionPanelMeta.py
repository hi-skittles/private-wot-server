# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AmmunitionPanelMeta.py
# Compiled at: 2014-10-01 12:00:53
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class AmmunitionPanelMeta(DAAPIModule):

    def setVehicleModule(self, newId, slotIdx, oldId, isRemove):
        self._printOverrideError('setVehicleModule')

    def showModuleInfo(self, moduleId):
        self._printOverrideError('showModuleInfo')

    def showTechnicalMaintenance(self):
        self._printOverrideError('showTechnicalMaintenance')

    def showCustomization(self):
        self._printOverrideError('showCustomization')

    def highlightParams(self, type):
        self._printOverrideError('highlightParams')

    def toRentContinue(self):
        self._printOverrideError('toRentContinue')

    def as_setDataS(self, data, type):
        return self.flashObject.as_setData(data, type) if self._isDAAPIInited() else None

    def as_setAmmoS(self, data):
        return self.flashObject.as_setAmmo(data) if self._isDAAPIInited() else None

    def as_setVehicleHasTurretS(self, hasTurret):
        return self.flashObject.as_setVehicleHasTurret(hasTurret) if self._isDAAPIInited() else None

    def as_setHistoricalBattleS(self, value):
        return self.flashObject.as_setHistoricalBattle(value) if self._isDAAPIInited() else None

    def as_setModulesEnabledS(self, value):
        return self.flashObject.as_setModulesEnabled(value) if self._isDAAPIInited() else None

    def as_updateVehicleStatusS(self, id, message, stateLevel, rentAvailable):
        return self.flashObject.as_updateVehicleStatus(id, message, stateLevel, rentAvailable) if self._isDAAPIInited() else None
