# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleLoadingMeta.py
# Compiled at: 2014-06-13 07:52:31
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BattleLoadingMeta(DAAPIModule):

    def onLoadComplete(self):
        self._printOverrideError('onLoadComplete')

    def as_setMapBGS(self, imgsource):
        return self.flashObject.as_setMapBG(imgsource) if self._isDAAPIInited() else None

    def as_setProgressS(self, val):
        return self.flashObject.as_setProgress(val) if self._isDAAPIInited() else None

    def as_setMapNameS(self, val):
        return self.flashObject.as_setMapName(val) if self._isDAAPIInited() else None

    def as_setBattleTypeNameS(self, name):
        return self.flashObject.as_setBattleTypeName(name) if self._isDAAPIInited() else None

    def as_setBattleTypeFrameNumS(self, frameNum):
        return self.flashObject.as_setBattleTypeFrameNum(frameNum) if self._isDAAPIInited() else None

    def as_setBattleTypeFrameNameS(self, frameName):
        return self.flashObject.as_setBattleTypeFrameName(frameName) if self._isDAAPIInited() else None

    def as_setWinTextS(self, val):
        return self.flashObject.as_setWinText(val) if self._isDAAPIInited() else None

    def as_setTeamsS(self, name1, name2):
        return self.flashObject.as_setTeams(name1, name2) if self._isDAAPIInited() else None

    def as_setTipS(self, val):
        return self.flashObject.as_setTip(val) if self._isDAAPIInited() else None

    def as_setTipTitleS(self, title):
        return self.flashObject.as_setTipTitle(title) if self._isDAAPIInited() else None

    def as_setPlayerDataS(self, playerVehicleID, prebattleID):
        return self.flashObject.as_setPlayerData(playerVehicleID, prebattleID) if self._isDAAPIInited() else None

    def as_setVehiclesDataS(self, isEnemy, vehiclesInfo):
        return self.flashObject.as_setVehiclesData(isEnemy, vehiclesInfo) if self._isDAAPIInited() else None

    def as_addVehicleInfoS(self, isEnemy, vehicleInfo, vehiclesIDs):
        return self.flashObject.as_addVehicleInfo(isEnemy, vehicleInfo, vehiclesIDs) if self._isDAAPIInited() else None

    def as_updateVehicleInfoS(self, isEnemy, vehicleInfo, vehiclesIDs):
        return self.flashObject.as_updateVehicleInfo(isEnemy, vehicleInfo, vehiclesIDs) if self._isDAAPIInited() else None

    def as_setVehicleStatusS(self, isEnemy, vehicleID, status, vehiclesIDs):
        return self.flashObject.as_setVehicleStatus(isEnemy, vehicleID, status, vehiclesIDs) if self._isDAAPIInited() else None

    def as_setPlayerStatusS(self, isEnemy, vehicleID, status):
        return self.flashObject.as_setPlayerStatus(isEnemy, vehicleID, status) if self._isDAAPIInited() else None
