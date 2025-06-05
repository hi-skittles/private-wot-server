# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WindowViewMeta.py
# Compiled at: 2014-12-08 06:09:37
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class WindowViewMeta(DAAPIModule):

    def onWindowMinimize(self):
        self._printOverrideError('onWindowMinimize')

    def onSourceLoaded(self):
        self._printOverrideError('onSourceLoaded')

    def onTryClosing(self):
        self._printOverrideError('onTryClosing')

    def as_getGeometryS(self):
        return self.flashObject.as_getGeometry() if self._isDAAPIInited() else None

    def as_setGeometryS(self, x, y, width, height):
        return self.flashObject.as_setGeometry(x, y, width, height) if self._isDAAPIInited() else None

    def as_isModalS(self):
        return self.flashObject.as_isModal() if self._isDAAPIInited() else None
