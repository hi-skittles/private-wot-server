# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/BaseDAAPIModuleMeta.py
# Compiled at: 2014-06-09 13:41:47
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BaseDAAPIModuleMeta(DAAPIModule):

    def as_isDAAPIInitedS(self):
        return self.flashObject.as_isDAAPIInited() if self._isDAAPIInited() else None

    def as_populateS(self):
        return self.flashObject.as_populate() if self._isDAAPIInited() else None

    def as_disposeS(self):
        return self.flashObject.as_dispose() if self._isDAAPIInited() else None
