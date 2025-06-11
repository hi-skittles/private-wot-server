# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/abstract.py
# Compiled at: 2015-03-30 10:03:56
import weakref
from gui.shared.utils import makeTupleByDict
from gui.battle_results import stats, items

class BattleResults(object):

    def __init__(self, results, dp):
        self._dp = weakref.proxy(dp)
        self._common = makeTupleByDict(stats.CommonInfo, results['common'])
        self._personal = makeTupleByDict(stats.PersonalInfo, results['personal'])

    def clear(self):
        pass

    @property
    def common(self):
        return self._common

    @property
    def personal(self):
        return self._personal

    def isWin(self):
        return self._common.winnerTeam == self._personal.team

    def requestTeamInfo(self, isMy, callback):
        callback(isMy, items.TeamInfo())

    def updateViewData(self, viewData):
        pass
