# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTabNavigatorMeta.py
# Compiled at: 2013-08-06 08:54:30
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileTabNavigatorMeta(DAAPIModule):

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None
