# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderInfoWindowMeta.py
# Compiled at: 2015-01-10 11:34:33
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortOrderInfoWindowMeta(DAAPIModule):

    def as_setWindowDataS(self, data):
        return self.flashObject.as_setWindowData(data) if self._isDAAPIInited() else None

    def as_setDynPropertiesS(self, data):
        return self.flashObject.as_setDynProperties(data) if self._isDAAPIInited() else None
