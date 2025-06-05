# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationUnitMeta.py
# Compiled at: 2015-01-23 05:02:23
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class StaticFormationUnitMeta(BaseRallyRoomView):

    def toggleStatusRequest(self):
        self._printOverrideError('toggleStatusRequest')

    def setRankedMode(self, isRanked):
        self._printOverrideError('setRankedMode')

    def showTeamCard(self):
        self._printOverrideError('showTeamCard')

    def as_closeSlotS(self, slotIdx, cost, slotsLabel):
        return self.flashObject.as_closeSlot(slotIdx, cost, slotsLabel) if self._isDAAPIInited() else None

    def as_openSlotS(self, slotIdx, canBeTaken, slotsLabel, compatibleVehiclesCount):
        return self.flashObject.as_openSlot(slotIdx, canBeTaken, slotsLabel, compatibleVehiclesCount) if self._isDAAPIInited() else None

    def as_setOpenedS(self, isOpened, statusLabel):
        return self.flashObject.as_setOpened(isOpened, statusLabel) if self._isDAAPIInited() else None

    def as_setTotalLabelS(self, hasTotalLevelError, totalLevelLabel, totalLevel):
        return self.flashObject.as_setTotalLabel(hasTotalLevelError, totalLevelLabel, totalLevel) if self._isDAAPIInited() else None

    def as_setLegionnairesCountS(self, legionnairesCount):
        return self.flashObject.as_setLegionnairesCount(legionnairesCount) if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_setTeamIconS(self, icon):
        return self.flashObject.as_setTeamIcon(icon) if self._isDAAPIInited() else None
