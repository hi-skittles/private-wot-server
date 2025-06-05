# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SquadViewMeta.py
# Compiled at: 2014-07-21 13:42:11
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class SquadViewMeta(BaseRallyRoomView):

    def leaveSquad(self):
        self._printOverrideError('leaveSquad')

    def as_updateBattleTypeS(self, battleTypeName):
        return self.flashObject.as_updateBattleType(battleTypeName) if self._isDAAPIInited() else None

    def as_updateInviteBtnStateS(self, isEnabled):
        return self.flashObject.as_updateInviteBtnState(isEnabled) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyButtonS(self, timer):
        return self.flashObject.as_setCoolDownForReadyButton(timer) if self._isDAAPIInited() else None
