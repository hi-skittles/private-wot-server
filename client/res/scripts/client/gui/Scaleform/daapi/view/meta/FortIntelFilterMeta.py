# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelFilterMeta.py
# Compiled at: 2014-09-25 04:11:30
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortIntelFilterMeta(DAAPIModule):

    def onTryToSearchByClanAbbr(self, tag, searchType):
        self._printOverrideError('onTryToSearchByClanAbbr')

    def onClearClanTagSearch(self):
        self._printOverrideError('onClearClanTagSearch')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setMaxClanAbbreviateLengthS(self, length):
        return self.flashObject.as_setMaxClanAbbreviateLength(length) if self._isDAAPIInited() else None

    def as_setSearchResultS(self, status):
        return self.flashObject.as_setSearchResult(status) if self._isDAAPIInited() else None

    def as_setFilterStatusS(self, filterStatus):
        return self.flashObject.as_setFilterStatus(filterStatus) if self._isDAAPIInited() else None

    def as_setFilterButtonStatusS(self, filterButtonStatus, showEffect):
        return self.flashObject.as_setFilterButtonStatus(filterButtonStatus, showEffect) if self._isDAAPIInited() else None

    def as_setupCooldownS(self, isOnCooldown):
        return self.flashObject.as_setupCooldown(isOnCooldown) if self._isDAAPIInited() else None

    def as_setClanAbbrevS(self, clanAbbrev):
        return self.flashObject.as_setClanAbbrev(clanAbbrev) if self._isDAAPIInited() else None
