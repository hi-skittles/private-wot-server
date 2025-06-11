# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationInvitesAndRequestsMeta.py
# Compiled at: 2015-01-05 07:30:51
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class StaticFormationInvitesAndRequestsMeta(DAAPIModule):

    def setDescription(self, value):
        self._printOverrideError('setDescription')

    def setShowOnlyInvites(self, value):
        self._printOverrideError('setShowOnlyInvites')

    def resolvePlayerRequest(self, playerId, playerAccepted):
        self._printOverrideError('resolvePlayerRequest')

    def as_getDataProviderS(self):
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_setStaticDataS(self, data):
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setTeamDescriptionS(self, description):
        return self.flashObject.as_setTeamDescription(description) if self._isDAAPIInited() else None
