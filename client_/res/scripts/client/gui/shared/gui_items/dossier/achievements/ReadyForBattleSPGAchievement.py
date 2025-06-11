# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleSPGAchievement.py
# Compiled at: 2015-02-27 03:53:53
from abstract import ClassProgressAchievement, getCompletedPotapovQuestsCount
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class ReadyForBattleSPGAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        self.__isCurrentUserAchievement = dossier.isCurrentUser() if dossier is not None else False
        super(ReadyForBattleSPGAchievement, self).__init__('readyForBattleSPG', _AB.TOTAL, dossier, value)
        return

    def getNextLevelInfo(self):
        return ('questsLeft', self._lvlUpValue if self.__isCurrentUserAchievement else 0)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'readyForBattleSPG')

    def _readCurrentProgressValue(self, dossier):
        return getCompletedPotapovQuestsCount(1, {'SPG'})
