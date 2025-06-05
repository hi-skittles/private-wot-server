# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortListMeta.py
# Compiled at: 2014-05-21 05:00:45
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyListView import BaseRallyListView

class FortListMeta(BaseRallyListView):

    def changeDivisionIndex(self, index):
        self._printOverrideError('changeDivisionIndex')

    def as_getDivisionsDPS(self):
        return self.flashObject.as_getDivisionsDP() if self._isDAAPIInited() else None

    def as_setSelectedDivisionS(self, index):
        return self.flashObject.as_setSelectedDivision(index) if self._isDAAPIInited() else None

    def as_setCreationEnabledS(self, value):
        return self.flashObject.as_setCreationEnabled(value) if self._isDAAPIInited() else None
