# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSellDialogMeta.py
# Compiled at: 2014-11-12 05:42:47
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class VehicleSellDialogMeta(DAAPIModule):

    def getDialogSettings(self):
        self._printOverrideError('getDialogSettings')

    def setDialogSettings(self, isOpen):
        self._printOverrideError('setDialogSettings')

    def sell(self, vehicleData, shells, eqs, optDevices, inventory, isDismissCrew):
        self._printOverrideError('sell')

    def setUserInput(self, value):
        self._printOverrideError('setUserInput')

    def setResultCredit(self, isGold, value):
        self._printOverrideError('setResultCredit')

    def checkControlQuestion(self, dismiss):
        self._printOverrideError('checkControlQuestion')

    def as_setDataS(self, vehicle, onVehicle, inInventory, removePrices, gold):
        return self.flashObject.as_setData(vehicle, onVehicle, inInventory, removePrices, gold) if self._isDAAPIInited() else None

    def as_checkGoldS(self, gold):
        return self.flashObject.as_checkGold(gold) if self._isDAAPIInited() else None

    def as_visibleControlBlockS(self, value):
        return self.flashObject.as_visibleControlBlock(value) if self._isDAAPIInited() else None

    def as_enableButtonS(self, value):
        return self.flashObject.as_enableButton(value) if self._isDAAPIInited() else None

    def as_setCtrlQuestionS(self, value):
        return self.flashObject.as_setCtrlQuestion(value) if self._isDAAPIInited() else None

    def as_setControlNumberS(self, isGold, value):
        return self.flashObject.as_setControlNumber(isGold, value) if self._isDAAPIInited() else None

    def as_cleanInputSummS(self):
        return self.flashObject.as_cleanInputSumm() if self._isDAAPIInited() else None
