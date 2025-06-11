# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTechniqueMeta.py
# Compiled at: 2013-09-26 12:04:15
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileTechniqueMeta(DAAPIModule):

    def as_responseVehicleDossierS(self, data):
        return self.flashObject.as_responseVehicleDossier(data) if self._isDAAPIInited() else None
