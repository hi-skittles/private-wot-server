# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleQueueMeta.py
# Compiled at: 2014-01-27 06:56:44
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BattleQueueMeta(DAAPIModule):

    def startClick(self):
        self._printOverrideError('startClick')

    def exitClick(self):
        self._printOverrideError('exitClick')

    def onEscape(self):
        self._printOverrideError('onEscape')

    def as_setTimerS(self, textLabel, timeLabel):
        return self.flashObject.as_setTimer(textLabel, timeLabel) if self._isDAAPIInited() else None

    def as_setTypeS(self, type):
        return self.flashObject.as_setType(type) if self._isDAAPIInited() else None

    def as_setPlayersS(self, text):
        return self.flashObject.as_setPlayers(text) if self._isDAAPIInited() else None

    def as_setListByTypeS(self, listData):
        return self.flashObject.as_setListByType(listData) if self._isDAAPIInited() else None

    def as_showStartS(self, vis):
        return self.flashObject.as_showStart(vis) if self._isDAAPIInited() else None

    def as_showExitS(self, vis):
        return self.flashObject.as_showExit(vis) if self._isDAAPIInited() else None
