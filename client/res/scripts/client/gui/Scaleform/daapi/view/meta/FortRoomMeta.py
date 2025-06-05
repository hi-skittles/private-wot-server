# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortRoomMeta.py
# Compiled at: 2015-03-11 04:49:34
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class FortRoomMeta(BaseRallyRoomView):

    def showChangeDivisionWindow(self):
        self._printOverrideError('showChangeDivisionWindow')

    def as_showLegionariesCountS(self, isShow, msg):
        return self.flashObject.as_showLegionariesCount(isShow, msg) if self._isDAAPIInited() else None

    def as_showLegionariesToolTipS(self, isShow):
        return self.flashObject.as_showLegionariesToolTip(isShow) if self._isDAAPIInited() else None

    def as_showOrdersBgS(self, isShow):
        return self.flashObject.as_showOrdersBg(isShow) if self._isDAAPIInited() else None
