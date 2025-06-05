# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortChoiceDivisionWindowMeta.py
# Compiled at: 2014-03-31 08:04:30
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortChoiceDivisionWindowMeta(DAAPIModule):

    def selectedDivision(self, divisionID):
        self._printOverrideError('selectedDivision')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
