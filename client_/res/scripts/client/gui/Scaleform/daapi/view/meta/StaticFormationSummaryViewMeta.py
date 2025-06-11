# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationSummaryViewMeta.py
# Compiled at: 2014-11-19 07:11:12
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class StaticFormationSummaryViewMeta(DAAPIModule):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
