# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/meta/TutorialBattleStatisticMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TutorialBattleStatisticMeta(DAAPIModule):

    def restart(self):
        self._printOverrideError('restart')

    def showVideoDialog(self):
        self._printOverrideError('showVideoDialog')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
