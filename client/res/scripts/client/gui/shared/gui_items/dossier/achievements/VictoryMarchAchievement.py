# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/VictoryMarchAchievement.py
# Compiled at: 2015-02-12 08:56:56
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SeriesAchievement

class VictoryMarchAchievement(SeriesAchievement):

    def __init__(self, dossier, value=None):
        super(VictoryMarchAchievement, self).__init__('victoryMarch', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.RATED_7X7, 'victoryMarchSeries'), (_AB.RATED_7X7, 'maxVictoryMarchSeries'))
