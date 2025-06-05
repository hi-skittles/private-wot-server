# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortCombatReservesIntroMeta.py
# Compiled at: 2014-12-16 10:14:05
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortCombatReservesIntroMeta(DAAPIModule):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
