# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CompanyMainWindowMeta.py
# Compiled at: 2014-07-21 13:42:11
from gui.Scaleform.daapi.view.lobby.rally.AbstractRallyWindow import AbstractRallyWindow

class CompanyMainWindowMeta(AbstractRallyWindow):

    def getCompanyName(self):
        self._printOverrideError('getCompanyName')

    def showFAQWindow(self):
        self._printOverrideError('showFAQWindow')

    def as_setWindowTitleS(self, title, icon):
        return self.flashObject.as_setWindowTitle(title, icon) if self._isDAAPIInited() else None
