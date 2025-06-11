# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileSummaryMeta.py
# Compiled at: 2013-09-17 06:43:23
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileSummaryMeta(DAAPIModule):

    def getPersonalScoreWarningText(self, data):
        self._printOverrideError('getPersonalScoreWarningText')

    def getGlobalRating(self, userName):
        self._printOverrideError('getGlobalRating')

    def as_setUserDataS(self, data):
        return self.flashObject.as_setUserData(data) if self._isDAAPIInited() else None
