# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ContextMenuManagerMeta.py
# Compiled at: 2014-12-02 09:22:47
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ContextMenuManagerMeta(DAAPIModule):

    def requestOptions(self, type, ctx):
        self._printOverrideError('requestOptions')

    def onOptionSelect(self, optionId):
        self._printOverrideError('onOptionSelect')

    def onHide(self):
        self._printOverrideError('onHide')

    def as_setOptionsS(self, data):
        return self.flashObject.as_setOptions(data) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
