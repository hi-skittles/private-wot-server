# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingCardPopoverMeta.py
# Compiled at: 2014-07-07 05:05:02
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortBuildingCardPopoverMeta(DAAPIModule):

    def openUpgradeWindow(self, value):
        self._printOverrideError('openUpgradeWindow')

    def openAssignedPlayersWindow(self, value):
        self._printOverrideError('openAssignedPlayersWindow')

    def openDemountBuildingWindow(self, value):
        self._printOverrideError('openDemountBuildingWindow')

    def openDirectionControlWindow(self):
        self._printOverrideError('openDirectionControlWindow')

    def openBuyOrderWindow(self):
        self._printOverrideError('openBuyOrderWindow')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setModernizationDestructionEnablingS(self, modernizationButtonEnabled, destroyButtonEnabled, modernizationButtonTooltip, destroyButtonTooltip):
        return self.flashObject.as_setModernizationDestructionEnabling(modernizationButtonEnabled, destroyButtonEnabled, modernizationButtonTooltip, destroyButtonTooltip) if self._isDAAPIInited() else None
