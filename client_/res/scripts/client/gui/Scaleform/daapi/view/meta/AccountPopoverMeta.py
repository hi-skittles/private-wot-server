# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AccountPopoverMeta.py
# Compiled at: 2014-09-15 07:41:05
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class AccountPopoverMeta(DAAPIModule):

    def openProfile(self):
        self._printOverrideError('openProfile')

    def openClanStatistic(self):
        self._printOverrideError('openClanStatistic')

    def openCrewStatistic(self):
        self._printOverrideError('openCrewStatistic')

    def openReferralManagement(self):
        self._printOverrideError('openReferralManagement')

    def as_setDataS(self, userData, isTeamKiller, mainAchievements, infoBtnEnabled, clanData, crewData):
        return self.flashObject.as_setData(userData, isTeamKiller, mainAchievements, infoBtnEnabled, clanData, crewData) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, emblemId):
        return self.flashObject.as_setClanEmblem(emblemId) if self._isDAAPIInited() else None

    def as_setCrewEmblemS(self, emblemId):
        return self.flashObject.as_setCrewEmblem(emblemId) if self._isDAAPIInited() else None

    def as_setReferralDataS(self, data):
        return self.flashObject.as_setReferralData(data) if self._isDAAPIInited() else None
