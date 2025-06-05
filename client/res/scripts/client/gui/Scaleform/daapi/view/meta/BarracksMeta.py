# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BarracksMeta.py
# Compiled at: 2014-04-18 12:21:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BarracksMeta(DAAPIModule):

    def invalidateTanksList(self):
        self._printOverrideError('invalidateTanksList')

    def setFilter(self, nation, role, tankType, location, nationID):
        self._printOverrideError('setFilter')

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        self._printOverrideError('onShowRecruitWindowClick')

    def unloadTankman(self, dataCompact):
        self._printOverrideError('unloadTankman')

    def dismissTankman(self, dataCompact):
        self._printOverrideError('dismissTankman')

    def buyBerths(self):
        self._printOverrideError('buyBerths')

    def closeBarracks(self):
        self._printOverrideError('closeBarracks')

    def setTankmenFilter(self):
        self._printOverrideError('setTankmenFilter')

    def openPersonalCase(self, value, tabNumber):
        self._printOverrideError('openPersonalCase')

    def as_setTankmenS(self, tankmenCount, placesCount, tankmenInBarracks, berthPrice, actionPriceData, berthBuyCount, tankmanArr):
        return self.flashObject.as_setTankmen(tankmenCount, placesCount, tankmenInBarracks, berthPrice, actionPriceData, berthBuyCount, tankmanArr) if self._isDAAPIInited() else None

    def as_updateTanksListS(self, provider):
        return self.flashObject.as_updateTanksList(provider) if self._isDAAPIInited() else None

    def as_setTankmenFilterS(self, nation, role, tankType, location, nationID):
        return self.flashObject.as_setTankmenFilter(nation, role, tankType, location, nationID) if self._isDAAPIInited() else None
