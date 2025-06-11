# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/view_helpers/emblems.py
# Compiled at: 2015-03-30 08:46:29
import BigWorld
import ResMgr
from functools import partial
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
from club_shared import EMBLEM_TYPE
from gui import GUI_SETTINGS
from gui.LobbyContext import g_lobbyContext
from gui.shared.utils import mapTextureToTheMemory
from gui.clubs import settings as club_settings

def _readClubEmblem(filePath):
    data = ResMgr.openSection(filePath)
    return data.asBinary if data is not None else None


def _getClubEmblemUrl(emblemID, size):
    try:
        urlPattern = GUI_SETTINGS.lookup('clubEmblems')
        if urlPattern and emblemID:
            return urlPattern % {'emblemID': emblemID,
             'size': size}
    except:
        LOG_CURRENT_EXCEPTION()

    return None


class _EmblemsHelper(object):

    @property
    def remoteCache(self):
        from gui.shared.RemoteDataDownloader import g_remoteCache
        return g_remoteCache

    @classmethod
    def getMemoryTexturePath(cls, emblem):
        return mapTextureToTheMemory(emblem)

    @classmethod
    def requestEmblemByUrl(cls, url, callback):
        if hasattr(BigWorld.player(), 'customFilesCache'):
            if url is not None:
                BigWorld.player().customFilesCache.get(url, lambda _, data: callback(data))
        else:
            LOG_WARNING('Trying to get emblem by url from non-account', url)
        return

    def _onEmblemReceived(self, emblemID, callback, handler, emblem):
        handler(emblemID, emblem)
        if callback is not None:
            callback(emblemID, emblem)
        return


class ClanEmblemsHelper(_EmblemsHelper):

    def requestClanEmblem32x32(self, clanDbID):
        svrSettings = g_lobbyContext.getServerSettings()
        if svrSettings:
            self.requestEmblemByUrl(svrSettings.fileServer.getClanEmblem32x32Url(clanDbID), partial(self.onClanEmblem32x32Received, clanDbID))

    def requestClanEmblem64x64(self, clanDbID):
        svrSettings = g_lobbyContext.getServerSettings()
        if svrSettings:
            self.requestEmblemByUrl(svrSettings.fileServer.getClanEmblem64x64Url(clanDbID), partial(self.onClanEmblem64x64Received, clanDbID))

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        pass

    def onClanEmblem64x64Received(self, clanDbID, emblem):
        pass


class ClubEmblemsHelper(_EmblemsHelper):
    _default = {EMBLEM_TYPE.SIZE_24x24: _readClubEmblem(club_settings.getDefaultEmblem24x24()),
     EMBLEM_TYPE.SIZE_32x32: _readClubEmblem(club_settings.getDefaultEmblem32x32()),
     EMBLEM_TYPE.SIZE_64x64: _readClubEmblem(club_settings.getDefaultEmblem64x64())}

    def requestClubEmblem24x24(self, clubDbID, emblemID, callback=None):
        proxy = partial(self._onEmblemReceived, clubDbID, callback, self.onClubEmblem24x24Received)
        url = _getClubEmblemUrl(emblemID, 24)
        if url:
            self.requestEmblemByUrl(url, proxy)
        else:
            self._doDefaultResponse(proxy, EMBLEM_TYPE.SIZE_24x24)

    def requestClubEmblem32x32(self, clubDbID, emblemID, callback=None):
        proxy = partial(self._onEmblemReceived, clubDbID, callback, self.onClubEmblem32x32Received)
        url = _getClubEmblemUrl(emblemID, 32)
        if url:
            self.requestEmblemByUrl(url, proxy)
        else:
            self._doDefaultResponse(proxy, EMBLEM_TYPE.SIZE_32x32)

    def requestClubEmblem64x64(self, clubDbID, emblemID, callback=None):
        proxy = partial(self._onEmblemReceived, clubDbID, callback, self.onClubEmblem64x64Received)
        url = _getClubEmblemUrl(emblemID, 64)
        if url:
            self.requestEmblemByUrl(url, proxy)
        else:
            self._doDefaultResponse(proxy, EMBLEM_TYPE.SIZE_64x64)

    def onClubEmblem24x24Received(self, clubDbID, emblem):
        pass

    def onClubEmblem32x32Received(self, clubDbID, emblem):
        pass

    def onClubEmblem64x64Received(self, clubDbID, emblem):
        pass

    def _doDefaultResponse(self, callback, size):
        BigWorld.callback(0.0, lambda : callback(self._default.get(size)))
