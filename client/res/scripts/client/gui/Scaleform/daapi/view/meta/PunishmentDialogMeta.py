# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PunishmentDialogMeta.py
# Compiled at: 2014-08-05 10:22:09
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class PunishmentDialogMeta(DAAPIModule):

    def as_setMsgTitleS(self, value):
        return self.flashObject.as_setMsgTitle(value) if self._isDAAPIInited() else None
