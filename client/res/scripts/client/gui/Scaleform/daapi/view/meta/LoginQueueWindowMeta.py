# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LoginQueueWindowMeta.py
# Compiled at: 2014-06-27 05:14:35
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LoginQueueWindowMeta(DAAPIModule):

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def onAutoLoginClick(self):
        self._printOverrideError('onAutoLoginClick')

    def as_setTitleS(self, title):
        return self.flashObject.as_setTitle(title) if self._isDAAPIInited() else None

    def as_setMessageS(self, message):
        return self.flashObject.as_setMessage(message) if self._isDAAPIInited() else None

    def as_setCancelLabelS(self, cancelLabel):
        return self.flashObject.as_setCancelLabel(cancelLabel) if self._isDAAPIInited() else None

    def as_showAutoLoginBtnS(self, value):
        return self.flashObject.as_showAutoLoginBtn(value) if self._isDAAPIInited() else None
