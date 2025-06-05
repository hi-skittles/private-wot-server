# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTechniquePageMeta.py
# Compiled at: 2013-12-11 11:13:59
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileTechniquePageMeta(DAAPIModule):

    def setIsInHangarSelected(self, value):
        self._printOverrideError('setIsInHangarSelected')

    def as_setSelectedVehicleIntCDS(self, index):
        return self.flashObject.as_setSelectedVehicleIntCD(index) if self._isDAAPIInited() else None
