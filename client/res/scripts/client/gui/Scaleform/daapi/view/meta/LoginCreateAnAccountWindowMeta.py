# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LoginCreateAnAccountWindowMeta.py
# Compiled at: 2013-08-30 04:11:48
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LoginCreateAnAccountWindowMeta(DAAPIModule):

    def onRegister(self, nickname):
        self._printOverrideError('onRegister')

    def as_updateTextsS(self, defValue, titleText, messageText, submitText):
        return self.flashObject.as_updateTexts(defValue, titleText, messageText, submitText) if self._isDAAPIInited() else None

    def as_registerResponseS(self, success, message):
        return self.flashObject.as_registerResponse(success, message) if self._isDAAPIInited() else None
