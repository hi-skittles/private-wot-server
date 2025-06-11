# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SimpleWindowMeta.py
# Compiled at: 2015-03-11 11:08:16
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class SimpleWindowMeta(DAAPIModule):

    def onBtnClick(self, action):
        self._printOverrideError('onBtnClick')

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_setTextS(self, header, descrition):
        return self.flashObject.as_setText(header, descrition) if self._isDAAPIInited() else None

    def as_setImageS(self, imgPath):
        return self.flashObject.as_setImage(imgPath) if self._isDAAPIInited() else None

    def as_setButtonsS(self, buttonsList, align, btnBottomMargin, btnWidth):
        return self.flashObject.as_setButtons(buttonsList, align, btnBottomMargin, btnWidth) if self._isDAAPIInited() else None
