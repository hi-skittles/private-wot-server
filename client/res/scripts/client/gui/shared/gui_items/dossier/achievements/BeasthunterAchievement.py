# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/BeasthunterAchievement.py
# Compiled at: 2014-08-13 11:09:18
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SimpleProgressAchievement

class BeasthunterAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value=None):
        super(BeasthunterAchievement, self).__init__('beasthunter', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'fragsBeast')
