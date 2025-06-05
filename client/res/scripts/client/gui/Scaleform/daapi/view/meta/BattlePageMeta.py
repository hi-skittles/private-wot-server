# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattlePageMeta.py
# Compiled at: 2015-01-30 04:05:58
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BattlePageMeta(DAAPIModule):

    def openTestWindow(self):
        self._printOverrideError('openTestWindow')

    def as_checkDAAPIS(self):
        return self.flashObject.as_checkDAAPI() if self._isDAAPIInited() else None
