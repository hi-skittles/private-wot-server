# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileSummaryWindow.py
# Compiled at: 2013-09-18 06:08:00
from adisp import process
from gui.Scaleform.daapi.view.lobby.profile.ProfileSummary import ProfileSummary
from gui.shared import g_itemsCache

class ProfileSummaryWindow(ProfileSummary):

    def __init__(self, *args):
        ProfileSummary.__init__(self, *args)
        self.__rating = 0

    def getGlobalRating(self, databaseID):
        if databaseID is not None:
            self._receiveRating(databaseID)
        return self.__rating

    @process
    def _receiveRating(self, databaseID):
        req = g_itemsCache.items.dossiers.getUserDossierRequester(int(databaseID))
        self.__rating = yield req.getGlobalRating()
