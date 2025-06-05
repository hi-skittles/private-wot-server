# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SimpleDialogMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class SimpleDialogMeta(DAAPIModule):

    def onButtonClick(self, buttonId):
        self._printOverrideError('onButtonClick')

    def as_setTextS(self, text):
        return self.flashObject.as_setText(text) if self._isDAAPIInited() else None

    def as_setTitleS(self, title):
        return self.flashObject.as_setTitle(title) if self._isDAAPIInited() else None

    def as_setButtonsS(self, buttonNames):
        return self.flashObject.as_setButtons(buttonNames) if self._isDAAPIInited() else None

    def as_setButtonEnablingS(self, id, isEnabled):
        return self.flashObject.as_setButtonEnabling(id, isEnabled) if self._isDAAPIInited() else None

    def as_setButtonFocusS(self, id):
        return self.flashObject.as_setButtonFocus(id) if self._isDAAPIInited() else None
