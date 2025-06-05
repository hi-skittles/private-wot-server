# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MinimapEntityMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class MinimapEntityMeta(DAAPIModule):

    def as_updatePointsS(self):
        return self.flashObject.as_updatePoints() if self._isDAAPIInited() else None
