# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceNotAvailableWindowMeta.py
# Compiled at: 2014-09-23 11:40:53
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortIntelligenceNotAvailableWindowMeta(DAAPIModule):

    def as_setDataS(self, value):
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None
