# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationStatsViewMeta.py
# Compiled at: 2014-11-19 02:48:45
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class StaticFormationStatsViewMeta(DAAPIModule):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
