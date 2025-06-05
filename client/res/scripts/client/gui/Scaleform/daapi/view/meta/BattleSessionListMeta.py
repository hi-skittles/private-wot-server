# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleSessionListMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BattleSessionListMeta(DAAPIModule):

    def requestToJoinTeam(self, prbID, prbType):
        self._printOverrideError('requestToJoinTeam')

    def getClientID(self):
        self._printOverrideError('getClientID')

    def as_refreshListS(self, data):
        return self.flashObject.as_refreshList(data) if self._isDAAPIInited() else None
