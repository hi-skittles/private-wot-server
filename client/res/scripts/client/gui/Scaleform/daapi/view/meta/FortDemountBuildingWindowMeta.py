# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDemountBuildingWindowMeta.py
# Compiled at: 2015-02-03 04:59:04
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortDemountBuildingWindowMeta(DAAPIModule):

    def applyDemount(self):
        self._printOverrideError('applyDemount')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
