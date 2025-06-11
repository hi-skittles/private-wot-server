# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileMeta.py
# Compiled at: 2013-08-06 08:54:30
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileMeta(DAAPIModule):

    def onCloseProfile(self):
        self._printOverrideError('onCloseProfile')

    def as_updateS(self, data):
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None
