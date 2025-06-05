# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/CrucialShotAchievement.py
# Compiled at: 2014-08-13 11:09:18
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SimpleProgressAchievement

class CrucialShotAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value=None):
        super(CrucialShotAchievement, self).__init__('crucialShotMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'crucialShot')
