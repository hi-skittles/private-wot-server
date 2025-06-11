# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortCreationCongratulationsWindowMeta.py
# Compiled at: 2014-02-07 03:40:46
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortCreationCongratulationsWindowMeta(DAAPIModule):

    def as_setTitleS(self, value):
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setTextS(self, value):
        return self.flashObject.as_setText(value) if self._isDAAPIInited() else None

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_setButtonLblS(self, value):
        return self.flashObject.as_setButtonLbl(value) if self._isDAAPIInited() else None
