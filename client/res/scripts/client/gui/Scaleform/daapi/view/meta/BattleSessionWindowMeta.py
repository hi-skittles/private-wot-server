# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleSessionWindowMeta.py
# Compiled at: 2014-10-27 10:35:29
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BattleSessionWindowMeta(DAAPIModule):

    def requestToAssignMember(self, accId):
        self._printOverrideError('requestToAssignMember')

    def requestToUnassignMember(self, accId):
        self._printOverrideError('requestToUnassignMember')

    def canMoveToAssigned(self):
        self._printOverrideError('canMoveToAssigned')

    def canMoveToUnassigned(self):
        self._printOverrideError('canMoveToUnassigned')

    def as_setStartTimeS(self, startTime):
        return self.flashObject.as_setStartTime(startTime) if self._isDAAPIInited() else None

    def as_setInfoS(self, wins, map, firstTeam, secondTeam, count, description, comment):
        return self.flashObject.as_setInfo(wins, map, firstTeam, secondTeam, count, description, comment) if self._isDAAPIInited() else None

    def as_setNationsLimitsS(self, nations):
        return self.flashObject.as_setNationsLimits(nations) if self._isDAAPIInited() else None

    def as_setClassesLimitsS(self, vehicleLevels, classesLimitsAreIdentical):
        return self.flashObject.as_setClassesLimits(vehicleLevels, classesLimitsAreIdentical) if self._isDAAPIInited() else None

    def as_setCommonLimitsS(self, teamLevel, minTotalLevel, maxTotalLevel, maxPlayers):
        return self.flashObject.as_setCommonLimits(teamLevel, minTotalLevel, maxTotalLevel, maxPlayers) if self._isDAAPIInited() else None

    def as_setPlayersCountTextS(self, playersCountText):
        return self.flashObject.as_setPlayersCountText(playersCountText) if self._isDAAPIInited() else None
