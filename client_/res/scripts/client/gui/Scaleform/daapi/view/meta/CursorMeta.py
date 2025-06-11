# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CursorMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class CursorMeta(DAAPIModule):

    def as_setCursorS(self, cursor):
        return self.flashObject.as_setCursor(cursor) if self._isDAAPIInited() else None
