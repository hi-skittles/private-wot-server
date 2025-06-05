# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ResearchPanelMeta.py
# Compiled at: 2014-09-30 10:53:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ResearchPanelMeta(DAAPIModule):

    def goToResearch(self):
        self._printOverrideError('goToResearch')

    def as_updateCurrentVehicleS(self, name, type, vDescription, earnedXP, isElite, isPremIGR):
        return self.flashObject.as_updateCurrentVehicle(name, type, vDescription, earnedXP, isElite, isPremIGR) if self._isDAAPIInited() else None

    def as_setEarnedXPS(self, earnedXP):
        return self.flashObject.as_setEarnedXP(earnedXP) if self._isDAAPIInited() else None

    def as_setEliteS(self, isElite):
        return self.flashObject.as_setElite(isElite) if self._isDAAPIInited() else None
