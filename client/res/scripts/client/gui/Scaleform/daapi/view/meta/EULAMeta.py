# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EULAMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class EULAMeta(DAAPIModule):

    def requestEULAText(self):
        self._printOverrideError('requestEULAText')

    def onLinkClick(self, url):
        self._printOverrideError('onLinkClick')

    def onApply(self):
        self._printOverrideError('onApply')

    def as_setEULATextS(self, text):
        return self.flashObject.as_setEULAText(text) if self._isDAAPIInited() else None
