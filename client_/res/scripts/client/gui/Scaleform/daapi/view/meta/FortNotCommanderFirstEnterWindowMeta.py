# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortNotCommanderFirstEnterWindowMeta.py
# Compiled at: 2014-08-12 03:54:48
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortNotCommanderFirstEnterWindowMeta(DAAPIModule):

    def as_setTitleS(self, value):
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setTextS(self, value):
        return self.flashObject.as_setText(value) if self._isDAAPIInited() else None

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_setButtonLblS(self, value):
        return self.flashObject.as_setButtonLbl(value) if self._isDAAPIInited() else None
