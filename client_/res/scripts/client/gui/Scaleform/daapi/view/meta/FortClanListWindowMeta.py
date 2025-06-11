# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortClanListWindowMeta.py
# Compiled at: 2014-03-18 13:32:31
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortClanListWindowMeta(DAAPIModule):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
