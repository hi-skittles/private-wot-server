# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceWindowMeta.py
# Compiled at: 2014-08-28 08:47:29
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortIntelligenceWindowMeta(DAAPIModule):

    def getLevelColumnIcons(self):
        self._printOverrideError('getLevelColumnIcons')

    def requestClanFortInfo(self, index):
        self._printOverrideError('requestClanFortInfo')

    def as_setClanFortInfoS(self, clanFortVO):
        return self.flashObject.as_setClanFortInfo(clanFortVO) if self._isDAAPIInited() else None

    def as_setDataS(self, value):
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None

    def as_setStatusTextS(self, statusText):
        return self.flashObject.as_setStatusText(statusText) if self._isDAAPIInited() else None

    def as_getSearchDPS(self):
        return self.flashObject.as_getSearchDP() if self._isDAAPIInited() else None

    def as_getCurrentListIndexS(self):
        return self.flashObject.as_getCurrentListIndex() if self._isDAAPIInited() else None

    def as_selectByIndexS(self, index):
        return self.flashObject.as_selectByIndex(index) if self._isDAAPIInited() else None
