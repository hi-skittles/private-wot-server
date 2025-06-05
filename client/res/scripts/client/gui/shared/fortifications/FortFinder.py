# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/fortifications/FortFinder.py
# Compiled at: 2014-10-17 18:02:12
import BigWorld
from gui.shared.utils.requesters import DataRequestsByIDProcessor, DataRequestCtx

class FortFinder(DataRequestsByIDProcessor):

    def getSender(self):
        return BigWorld.player()

    def request(self, filterType, abbrevPattern, homePeripheryID, limit, lvlFrom, lvlTo, ownStartDefHourFrom, ownStartDefHourTo, nextOwnStartDefHourFrom, nextOwnStartDefHourTo, defHourChangeDay, extStartDefHourFrom, extStartDefHourTo, attackDay, ownFortLvl, ownProfitFactor10, avgBuildingLevel10, ownBattleCountForFort, firstDefaultQuery, electedClanDBIDs, callback=None):
        return self.doRequestEx(DataRequestCtx(), callback, 'requestFortPublicInfo', filterType, abbrevPattern, homePeripheryID, limit, lvlFrom, lvlTo, ownStartDefHourFrom, ownStartDefHourTo, nextOwnStartDefHourFrom, nextOwnStartDefHourTo, defHourChangeDay, extStartDefHourFrom, extStartDefHourTo, attackDay, ownFortLvl, ownProfitFactor10, avgBuildingLevel10, ownBattleCountForFort, firstDefaultQuery, electedClanDBIDs)

    def response(self, requestID, result, data):
        self._onResponseReceived(requestID, result, data)
