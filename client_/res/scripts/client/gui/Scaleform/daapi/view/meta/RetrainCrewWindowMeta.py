# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RetrainCrewWindowMeta.py
# Compiled at: 2014-01-23 08:46:21
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class RetrainCrewWindowMeta(DAAPIModule):

    def submit(self, data):
        self._printOverrideError('submit')

    def changeRetrainType(self, retrainTypeIndex):
        self._printOverrideError('changeRetrainType')

    def as_setCommonDataS(self, data):
        return self.flashObject.as_setCommonData(data) if self._isDAAPIInited() else None

    def as_updateDataS(self, data):
        return self.flashObject.as_updateData(data) if self._isDAAPIInited() else None
