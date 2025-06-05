# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ToolTipMgrMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ToolTipMgrMeta(DAAPIModule):

    def onCreateComplexTooltip(self, tooltipId, stateType):
        self._printOverrideError('onCreateComplexTooltip')

    def onCreateTypedTooltip(self, type, args, stateType):
        self._printOverrideError('onCreateTypedTooltip')

    def as_showS(self, tooltipData, linkage):
        return self.flashObject.as_show(tooltipData, linkage) if self._isDAAPIInited() else None
