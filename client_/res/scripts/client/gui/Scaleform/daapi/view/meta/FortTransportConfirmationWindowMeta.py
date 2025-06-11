# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortTransportConfirmationWindowMeta.py
# Compiled at: 2015-02-11 07:47:24
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortTransportConfirmationWindowMeta(DAAPIModule):

    def onCancel(self):
        self._printOverrideError('onCancel')

    def onTransporting(self, size):
        self._printOverrideError('onTransporting')

    def as_setMaxTransportingSizeS(self, maxSizeStr):
        return self.flashObject.as_setMaxTransportingSize(maxSizeStr) if self._isDAAPIInited() else None

    def as_setFooterTextS(self, text):
        return self.flashObject.as_setFooterText(text) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_enableForFirstTransportingS(self, isFirstTransporting):
        return self.flashObject.as_enableForFirstTransporting(isFirstTransporting) if self._isDAAPIInited() else None
