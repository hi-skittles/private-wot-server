# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WaitingViewMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class WaitingViewMeta(DAAPIModule):

    def showS(self, data):
        return self.flashObject.show(data) if self._isDAAPIInited() else None

    def hideS(self, data):
        return self.flashObject.hide(data) if self._isDAAPIInited() else None
