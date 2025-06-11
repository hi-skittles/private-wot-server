# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IconDialogMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class IconDialogMeta(DAAPIModule):

    def as_setIconS(self, path):
        return self.flashObject.as_setIcon(path) if self._isDAAPIInited() else None
