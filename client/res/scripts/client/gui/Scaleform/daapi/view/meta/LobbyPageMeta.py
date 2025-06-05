# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyPageMeta.py
# Compiled at: 2015-01-30 04:05:58
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LobbyPageMeta(DAAPIModule):

    def moveSpace(self, x, y, delta):
        self._printOverrideError('moveSpace')

    def getSubContainerType(self):
        self._printOverrideError('getSubContainerType')

    def as_showHelpLayoutS(self):
        return self.flashObject.as_showHelpLayout() if self._isDAAPIInited() else None

    def as_closeHelpLayoutS(self):
        return self.flashObject.as_closeHelpLayout() if self._isDAAPIInited() else None
