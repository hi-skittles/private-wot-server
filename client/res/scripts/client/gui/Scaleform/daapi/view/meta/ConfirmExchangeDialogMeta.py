# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ConfirmExchangeDialogMeta.py
# Compiled at: 2014-12-11 09:02:03
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ConfirmExchangeDialogMeta(DAAPIModule):

    def exchange(self, goldValue):
        self._printOverrideError('exchange')

    def as_updateS(self, data):
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None
