# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortModernizationWindowMeta.py
# Compiled at: 2014-12-24 08:33:34
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortModernizationWindowMeta(DAAPIModule):

    def applyAction(self):
        self._printOverrideError('applyAction')

    def openOrderDetailsWindow(self):
        self._printOverrideError('openOrderDetailsWindow')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_applyButtonLblS(self, value):
        return self.flashObject.as_applyButtonLbl(value) if self._isDAAPIInited() else None

    def as_cancelButtonS(self, value):
        return self.flashObject.as_cancelButton(value) if self._isDAAPIInited() else None

    def as_windowTitleS(self, value):
        return self.flashObject.as_windowTitle(value) if self._isDAAPIInited() else None
