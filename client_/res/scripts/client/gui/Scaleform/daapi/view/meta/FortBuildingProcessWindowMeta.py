# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingProcessWindowMeta.py
# Compiled at: 2014-03-06 11:13:54
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortBuildingProcessWindowMeta(DAAPIModule):

    def requestBuildingInfo(self, uid):
        self._printOverrideError('requestBuildingInfo')

    def applyBuildingProcess(self, uid):
        self._printOverrideError('applyBuildingProcess')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_responseBuildingInfoS(self, data):
        return self.flashObject.as_responseBuildingInfo(data) if self._isDAAPIInited() else None
