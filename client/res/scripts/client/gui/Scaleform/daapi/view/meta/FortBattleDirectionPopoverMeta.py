# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBattleDirectionPopoverMeta.py
# Compiled at: 2014-06-10 04:58:26
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortBattleDirectionPopoverMeta(DAAPIModule):

    def requestToJoin(self, fortBattleID):
        self._printOverrideError('requestToJoin')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
