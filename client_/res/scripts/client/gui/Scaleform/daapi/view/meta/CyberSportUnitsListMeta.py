# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportUnitsListMeta.py
# Compiled at: 2015-03-04 07:16:03
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyListView import BaseRallyListView

class CyberSportUnitsListMeta(BaseRallyListView):

    def getTeamData(self, index):
        self._printOverrideError('getTeamData')

    def refreshTeams(self):
        self._printOverrideError('refreshTeams')

    def filterVehicles(self):
        self._printOverrideError('filterVehicles')

    def setTeamFilters(self, showOnlyStatic):
        self._printOverrideError('setTeamFilters')

    def loadPrevious(self):
        self._printOverrideError('loadPrevious')

    def loadNext(self):
        self._printOverrideError('loadNext')

    def showRallyProfile(self, id):
        self._printOverrideError('showRallyProfile')

    def as_setSearchResultTextS(self, text, descrText, filterData):
        return self.flashObject.as_setSearchResultText(text, descrText, filterData) if self._isDAAPIInited() else None

    def as_setHeaderS(self, data):
        return self.flashObject.as_setHeader(data) if self._isDAAPIInited() else None

    def as_setSelectedVehiclesInfoS(self, infoText, selectedVehiclesCount):
        return self.flashObject.as_setSelectedVehiclesInfo(infoText, selectedVehiclesCount) if self._isDAAPIInited() else None

    def as_updateNavigationBlockS(self, value):
        return self.flashObject.as_updateNavigationBlock(value) if self._isDAAPIInited() else None

    def as_updateRallyIconS(self, iconPath):
        return self.flashObject.as_updateRallyIcon(iconPath) if self._isDAAPIInited() else None
