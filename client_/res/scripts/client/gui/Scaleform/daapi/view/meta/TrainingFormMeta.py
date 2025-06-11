# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TrainingFormMeta.py
# Compiled at: 2014-08-11 04:08:07
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TrainingFormMeta(DAAPIModule):

    def joinTrainingRequest(self, id):
        self._printOverrideError('joinTrainingRequest')

    def createTrainingRequest(self):
        self._printOverrideError('createTrainingRequest')

    def onEscape(self):
        self._printOverrideError('onEscape')

    def onLeave(self):
        self._printOverrideError('onLeave')

    def as_setListS(self, provider, totalPlayers):
        return self.flashObject.as_setList(provider, totalPlayers) if self._isDAAPIInited() else None
