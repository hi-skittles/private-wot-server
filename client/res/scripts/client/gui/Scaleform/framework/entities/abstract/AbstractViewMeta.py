# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/AbstractViewMeta.py
# Compiled at: 2014-06-05 07:36:06
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class AbstractViewMeta(DAAPIModule):

    def registerFlashComponent(self, component, alias):
        self._printOverrideError('registerFlashComponent')

    def unregisterFlashComponent(self, alias):
        self._printOverrideError('unregisterFlashComponent')

    def onFocusIn(self, alias):
        self._printOverrideError('onFocusIn')

    def as_populateS(self):
        return self.flashObject.as_populate() if self._isDAAPIInited() else None

    def as_disposeS(self):
        return self.flashObject.as_dispose() if self._isDAAPIInited() else None
