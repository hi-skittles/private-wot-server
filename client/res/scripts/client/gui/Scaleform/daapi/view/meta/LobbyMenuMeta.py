# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyMenuMeta.py
# Compiled at: 2014-11-05 06:08:13
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LobbyMenuMeta(DAAPIModule):

    def settingsClick(self):
        self._printOverrideError('settingsClick')

    def cancelClick(self):
        self._printOverrideError('cancelClick')

    def refuseTraining(self):
        self._printOverrideError('refuseTraining')

    def logoffClick(self):
        self._printOverrideError('logoffClick')

    def quitClick(self):
        self._printOverrideError('quitClick')

    def versionInfoClick(self):
        self._printOverrideError('versionInfoClick')

    def as_setVersionMessageS(self, message, showLinkButton):
        return self.flashObject.as_setVersionMessage(message, showLinkButton) if self._isDAAPIInited() else None
