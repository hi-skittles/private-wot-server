# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DismissTankmanDialogMeta.py
# Compiled at: 2014-03-12 09:43:33
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class DismissTankmanDialogMeta(DAAPIModule):

    def as_tankManS(self, value):
        return self.flashObject.as_tankMan(value) if self._isDAAPIInited() else None
