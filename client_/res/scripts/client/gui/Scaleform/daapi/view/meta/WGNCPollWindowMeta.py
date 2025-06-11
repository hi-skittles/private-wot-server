# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WGNCPollWindowMeta.py
# Compiled at: 2015-02-09 03:23:57
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class WGNCPollWindowMeta(DAAPIModule):

    def onBtnClick(self):
        self._printOverrideError('onBtnClick')

    def onLinkClick(self, actions):
        self._printOverrideError('onLinkClick')

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_setTextS(self, value):
        return self.flashObject.as_setText(value) if self._isDAAPIInited() else None

    def as_setButtonLblS(self, value):
        return self.flashObject.as_setButtonLbl(value) if self._isDAAPIInited() else None
