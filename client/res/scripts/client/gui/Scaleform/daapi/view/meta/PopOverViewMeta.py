# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PopOverViewMeta.py
# Compiled at: 2013-12-18 09:16:28
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class PopOverViewMeta(DAAPIModule):

    def as_setArrowDirectionS(self, value):
        return self.flashObject.as_setArrowDirection(value) if self._isDAAPIInited() else None

    def as_setArrowPositionS(self, value):
        return self.flashObject.as_setArrowPosition(value) if self._isDAAPIInited() else None
