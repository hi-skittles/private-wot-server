# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarMeta.py
# Compiled at: 2015-01-19 04:54:27
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class HangarMeta(DAAPIModule):

    def onEscape(self):
        self._printOverrideError('onEscape')

    def checkMoney(self):
        self._printOverrideError('checkMoney')

    def showHelpLayout(self):
        self._printOverrideError('showHelpLayout')

    def closeHelpLayout(self):
        self._printOverrideError('closeHelpLayout')

    def toggleGUIEditor(self):
        self._printOverrideError('toggleGUIEditor')

    def as_setCrewEnabledS(self, value):
        return self.flashObject.as_setCrewEnabled(value) if self._isDAAPIInited() else None

    def as_setCarouselEnabledS(self, value):
        return self.flashObject.as_setCarouselEnabled(value) if self._isDAAPIInited() else None

    def as_setupAmmunitionPanelS(self, maintenanceEnabled, customizationEnabled):
        return self.flashObject.as_setupAmmunitionPanel(maintenanceEnabled, customizationEnabled) if self._isDAAPIInited() else None

    def as_setControlsVisibleS(self, value):
        return self.flashObject.as_setControlsVisible(value) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

    def as_showHelpLayoutS(self):
        return self.flashObject.as_showHelpLayout() if self._isDAAPIInited() else None

    def as_closeHelpLayoutS(self):
        return self.flashObject.as_closeHelpLayout() if self._isDAAPIInited() else None

    def as_setIsIGRS(self, value, text):
        return self.flashObject.as_setIsIGR(value, text) if self._isDAAPIInited() else None

    def as_setServerStatsS(self, stats, tooltipType):
        return self.flashObject.as_setServerStats(stats, tooltipType) if self._isDAAPIInited() else None

    def as_setServerStatsInfoS(self, tooltipFullData):
        return self.flashObject.as_setServerStatsInfo(tooltipFullData) if self._isDAAPIInited() else None

    def as_setVehicleIGRS(self, actionIgrDaysLeft):
        return self.flashObject.as_setVehicleIGR(actionIgrDaysLeft) if self._isDAAPIInited() else None
