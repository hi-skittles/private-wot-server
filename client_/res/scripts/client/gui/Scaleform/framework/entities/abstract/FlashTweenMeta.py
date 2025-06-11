# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/FlashTweenMeta.py
# Compiled at: 2014-03-28 03:49:00
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FlashTweenMeta(DAAPIModule):

    def moveOnPositionS(self, percent):
        return self.flashObject.moveOnPosition(percent) if self._isDAAPIInited() else None
