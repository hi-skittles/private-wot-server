# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsCurrentTabMeta.py
# Compiled at: 2013-12-20 04:57:29
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsCurrentTabMeta(DAAPIModule):

    def sort(self, type, hideDone):
        self._printOverrideError('sort')

    def getQuestInfo(self, questID):
        self._printOverrideError('getQuestInfo')

    def getSortedTableData(self, tableData):
        self._printOverrideError('getSortedTableData')

    def as_setQuestsDataS(self, data, totalTasks):
        return self.flashObject.as_setQuestsData(data, totalTasks) if self._isDAAPIInited() else None

    def as_setSelectedQuestS(self, questID):
        return self.flashObject.as_setSelectedQuest(questID) if self._isDAAPIInited() else None
