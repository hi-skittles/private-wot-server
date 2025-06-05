# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsPersonalWelcomeViewMeta.py
# Compiled at: 2014-10-27 12:14:02
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsPersonalWelcomeViewMeta(DAAPIModule):

    def success(self):
        self._printOverrideError('success')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
