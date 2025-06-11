# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsTileChainsViewMeta.py
# Compiled at: 2014-11-10 10:28:23
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsTileChainsViewMeta(DAAPIModule):

    def getTileData(self, vehicleType, taskFilterType, hideCompleted):
        self._printOverrideError('getTileData')

    def getChainProgress(self):
        self._printOverrideError('getChainProgress')

    def getTaskDetails(self, taskId):
        self._printOverrideError('getTaskDetails')

    def selectTask(self, taskId):
        self._printOverrideError('selectTask')

    def refuseTask(self, taskId):
        self._printOverrideError('refuseTask')

    def gotoBack(self):
        self._printOverrideError('gotoBack')

    def showAwardVehicleInfo(self, awardVehicleID):
        self._printOverrideError('showAwardVehicleInfo')

    def showAwardVehicleInHangar(self, awardVehicleID):
        self._printOverrideError('showAwardVehicleInHangar')

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_updateTileDataS(self, data):
        return self.flashObject.as_updateTileData(data) if self._isDAAPIInited() else None

    def as_updateChainProgressS(self, data):
        return self.flashObject.as_updateChainProgress(data) if self._isDAAPIInited() else None

    def as_updateTaskDetailsS(self, data):
        return self.flashObject.as_updateTaskDetails(data) if self._isDAAPIInited() else None

    def as_setSelectedTaskS(self, taskId):
        return self.flashObject.as_setSelectedTask(taskId) if self._isDAAPIInited() else None
