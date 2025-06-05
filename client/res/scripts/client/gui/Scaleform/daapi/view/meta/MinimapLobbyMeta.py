# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MinimapLobbyMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class MinimapLobbyMeta(DAAPIModule):

    def setMap(self, arenaID):
        self._printOverrideError('setMap')

    def as_changeMapS(self, texture):
        return self.flashObject.as_changeMap(texture) if self._isDAAPIInited() else None

    def as_addPointS(self, x, y, type, color, id):
        return self.flashObject.as_addPoint(x, y, type, color, id) if self._isDAAPIInited() else None

    def as_clearS(self):
        return self.flashObject.as_clear() if self._isDAAPIInited() else None
