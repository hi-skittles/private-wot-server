# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/TitleSniperAchievement.py
# Compiled at: 2014-08-13 11:09:18
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SeriesAchievement

class TitleSniperAchievement(SeriesAchievement):

    def __init__(self, dossier, value=None):
        super(TitleSniperAchievement, self).__init__('titleSniper', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'sniperSeries'), (_AB.TOTAL, 'maxSniperSeries'))
