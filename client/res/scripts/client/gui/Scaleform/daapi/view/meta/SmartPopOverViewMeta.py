# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SmartPopOverViewMeta.py
# Compiled at: 2013-12-18 07:25:03
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class SmartPopOverViewMeta(DAAPIModule):

    def as_setPositionKeyPointS(self, valX, valY):
        return self.flashObject.as_setPositionKeyPoint(valX, valY) if self._isDAAPIInited() else None
