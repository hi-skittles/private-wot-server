# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleResultsMeta.py
# Compiled at: 2015-03-30 10:03:56
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BattleResultsMeta(DAAPIModule):

    def saveSorting(self, iconType, sortDirection, bonusType):
        self._printOverrideError('saveSorting')

    def showEventsWindow(self, questID, eventType):
        self._printOverrideError('showEventsWindow')

    def getClanEmblem(self, uid, clanID):
        self._printOverrideError('getClanEmblem')

    def getTeamEmblem(self, uid, teamID, isUseHtmlWrap):
        self._printOverrideError('getTeamEmblem')

    def startCSAnimationSound(self):
        self._printOverrideError('startCSAnimationSound')

    def onResultsSharingBtnPress(self):
        self._printOverrideError('onResultsSharingBtnPress')

    def onTeamCardClick(self, teamDBID):
        self._printOverrideError('onTeamCardClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, uid, iconTag):
        return self.flashObject.as_setClanEmblem(uid, iconTag) if self._isDAAPIInited() else None

    def as_setTeamInfoS(self, uid, iconTag, teamName):
        return self.flashObject.as_setTeamInfo(uid, iconTag, teamName) if self._isDAAPIInited() else None

    def as_setAnimationS(self, data):
        return self.flashObject.as_setAnimation(data) if self._isDAAPIInited() else None
