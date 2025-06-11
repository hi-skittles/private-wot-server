# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileSectionMeta.py
# Compiled at: 2013-09-23 11:19:10
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileSectionMeta(DAAPIModule):

    def setActive(self, value):
        self._printOverrideError('setActive')

    def requestData(self, data):
        self._printOverrideError('requestData')

    def requestDossier(self, type):
        self._printOverrideError('requestDossier')

    def as_updateS(self, data):
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_responseDossierS(self, type, data):
        return self.flashObject.as_responseDossier(type, data) if self._isDAAPIInited() else None
