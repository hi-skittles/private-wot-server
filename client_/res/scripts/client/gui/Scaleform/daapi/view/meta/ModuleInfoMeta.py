# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ModuleInfoMeta.py
# Compiled at: 2014-12-15 09:22:53
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ModuleInfoMeta(DAAPIModule):

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def onActionButtonClick(self):
        self._printOverrideError('onActionButtonClick')

    def as_setModuleInfoS(self, moduleInfo):
        return self.flashObject.as_setModuleInfo(moduleInfo) if self._isDAAPIInited() else None

    def as_setActionButtonS(self, data):
        return self.flashObject.as_setActionButton(data) if self._isDAAPIInited() else None
