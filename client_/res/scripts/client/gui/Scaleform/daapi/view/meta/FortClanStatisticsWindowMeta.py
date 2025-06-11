# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortClanStatisticsWindowMeta.py
# Compiled at: 2014-03-10 13:38:05
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortClanStatisticsWindowMeta(DAAPIModule):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
