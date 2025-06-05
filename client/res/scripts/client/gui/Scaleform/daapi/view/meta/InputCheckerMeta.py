# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/InputCheckerMeta.py
# Compiled at: 2014-03-11 11:37:44
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class InputCheckerMeta(DAAPIModule):

    def sendUserInput(self, value, isValidSyntax):
        self._printOverrideError('sendUserInput')

    def as_setTitleS(self, value):
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setBodyS(self, value):
        return self.flashObject.as_setBody(value) if self._isDAAPIInited() else None

    def as_setErrorMsgS(self, value):
        return self.flashObject.as_setErrorMsg(value) if self._isDAAPIInited() else None

    def as_setFormattedControlNumberS(self, value):
        return self.flashObject.as_setFormattedControlNumber(value) if self._isDAAPIInited() else None

    def as_setOriginalControlNumberS(self, value):
        return self.flashObject.as_setOriginalControlNumber(value) if self._isDAAPIInited() else None

    def as_invalidUserTextS(self, value):
        return self.flashObject.as_invalidUserText(value) if self._isDAAPIInited() else None
