# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingComponentMeta.py
# Compiled at: 2014-06-04 10:53:08
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortBuildingComponentMeta(DAAPIModule):

    def onTransportingRequest(self, exportFrom, importTo):
        self._printOverrideError('onTransportingRequest')

    def requestBuildingProcess(self, direction, position):
        self._printOverrideError('requestBuildingProcess')

    def upgradeVisitedBuilding(self, uid):
        self._printOverrideError('upgradeVisitedBuilding')

    def getBuildingTooltipData(self, uid):
        self._printOverrideError('getBuildingTooltipData')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setBuildingDataS(self, data):
        return self.flashObject.as_setBuildingData(data) if self._isDAAPIInited() else None

    def as_refreshTransportingS(self):
        return self.flashObject.as_refreshTransporting() if self._isDAAPIInited() else None
