# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortFixedPlayersWindowMeta.py
# Compiled at: 2014-03-04 08:47:42
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortFixedPlayersWindowMeta(DAAPIModule):

    def assignToBuilding(self):
        self._printOverrideError('assignToBuilding')

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
