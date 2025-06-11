# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WrapperViewMeta.py
# Compiled at: 2014-12-08 06:09:37
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class WrapperViewMeta(DAAPIModule):

    def onWindowClose(self):
        self._printOverrideError('onWindowClose')

    def as_showWaitingS(self, msg, props):
        return self.flashObject.as_showWaiting(msg, props) if self._isDAAPIInited() else None

    def as_hideWaitingS(self):
        return self.flashObject.as_hideWaiting() if self._isDAAPIInited() else None
