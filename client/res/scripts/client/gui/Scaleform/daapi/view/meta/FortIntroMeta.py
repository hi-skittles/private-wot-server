# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntroMeta.py
# Compiled at: 2014-05-07 05:23:45
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyIntroView import BaseRallyIntroView

class FortIntroMeta(BaseRallyIntroView):

    def as_setIntroDataS(self, data):
        return self.flashObject.as_setIntroData(data) if self._isDAAPIInited() else None
