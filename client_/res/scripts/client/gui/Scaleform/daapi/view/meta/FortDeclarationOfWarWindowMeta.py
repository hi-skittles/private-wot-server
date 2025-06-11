# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDeclarationOfWarWindowMeta.py
# Compiled at: 2014-08-01 09:02:06
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortDeclarationOfWarWindowMeta(DAAPIModule):

    def onDirectonChosen(self, directionUID):
        self._printOverrideError('onDirectonChosen')

    def onDirectionSelected(self):
        self._printOverrideError('onDirectionSelected')

    def as_setupHeaderS(self, title, description):
        return self.flashObject.as_setupHeader(title, description) if self._isDAAPIInited() else None

    def as_setupClansS(self, myClan, enemyClan):
        return self.flashObject.as_setupClans(myClan, enemyClan) if self._isDAAPIInited() else None

    def as_setDirectionsS(self, data):
        return self.flashObject.as_setDirections(data) if self._isDAAPIInited() else None

    def as_selectDirectionS(self, uid):
        return self.flashObject.as_selectDirection(uid) if self._isDAAPIInited() else None
