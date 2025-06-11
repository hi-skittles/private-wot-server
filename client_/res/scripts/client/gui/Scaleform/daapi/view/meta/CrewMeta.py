# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrewMeta.py
# Compiled at: 2015-03-11 11:08:16
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class CrewMeta(DAAPIModule):

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        self._printOverrideError('onShowRecruitWindowClick')

    def unloadAllTankman(self):
        self._printOverrideError('unloadAllTankman')

    def equipTankman(self, tankmanID, slot):
        self._printOverrideError('equipTankman')

    def updateTankmen(self):
        self._printOverrideError('updateTankmen')

    def openPersonalCase(self, value, tabNumber):
        self._printOverrideError('openPersonalCase')

    def onCrewDogMoreInfoClick(self):
        self._printOverrideError('onCrewDogMoreInfoClick')

    def onCrewDogItemClick(self):
        self._printOverrideError('onCrewDogItemClick')

    def as_tankmenResponseS(self, roles, tankmen):
        return self.flashObject.as_tankmenResponse(roles, tankmen) if self._isDAAPIInited() else None

    def as_dogResponseS(self, dogName):
        return self.flashObject.as_dogResponse(dogName) if self._isDAAPIInited() else None
