# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/CaptchaDialogMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
from gui.shared import events

class CaptchaDialogMeta(IDialogMeta):

    def __init__(self, errorText=None):
        self.__errorText = errorText

    def hasError(self):
        return self.__errorText is not None and len(self.__errorText)

    def getErrorText(self):
        return self.__errorText

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_CAPTCHA_DIALOG
