# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/KampferAchievement.py
# Compiled at: 2014-08-28 07:45:25
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import ClassProgressAchievement
from abstract.mixins import Fortification

class KampferAchievement(Fortification, ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        ClassProgressAchievement.__init__(self, 'kampfer', _AB.FORT, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FORT, 'kampfer')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FORT, 'wins')
