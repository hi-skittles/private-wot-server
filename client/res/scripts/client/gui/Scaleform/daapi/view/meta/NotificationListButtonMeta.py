# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationListButtonMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class NotificationListButtonMeta(DAAPIModule):

    def handleClick(self):
        self._printOverrideError('handleClick')

    def as_setStateS(self, isBlinking):
        return self.flashObject.as_setState(isBlinking) if self._isDAAPIInited() else None
