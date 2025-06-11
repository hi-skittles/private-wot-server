# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/PopoverManagerMeta.py
# Compiled at: 2014-07-08 13:59:29
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class PopoverManagerMeta(DAAPIModule):

    def requestShowPopover(self, alias, data):
        self._printOverrideError('requestShowPopover')

    def requestHidePopover(self):
        self._printOverrideError('requestHidePopover')

    def as_onPopoverDestroyS(self):
        return self.flashObject.as_onPopoverDestroy() if self._isDAAPIInited() else None
