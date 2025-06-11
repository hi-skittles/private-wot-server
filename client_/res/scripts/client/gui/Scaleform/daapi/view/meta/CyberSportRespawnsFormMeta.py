# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportRespawnsFormMeta.py
# Compiled at: 2015-01-10 07:45:59
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class CyberSportRespawnsFormMeta(BaseRallyRoomView):

    def onReadyClick(self, userID):
        self._printOverrideError('onReadyClick')

    def as_setMapBGS(self, imgsource):
        return self.flashObject.as_setMapBG(imgsource) if self._isDAAPIInited() else None

    def as_setProgressS(self, time):
        return self.flashObject.as_setProgress(time) if self._isDAAPIInited() else None
