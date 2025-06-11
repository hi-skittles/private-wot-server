# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsSeasonsViewMeta.py
# Compiled at: 2014-10-30 14:08:07
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsSeasonsViewMeta(DAAPIModule):

    def onShowAwardsClick(self, seasonID):
        self._printOverrideError('onShowAwardsClick')

    def onTileClick(self, tileID):
        self._printOverrideError('onTileClick')

    def onSlotClick(self, slotID):
        self._printOverrideError('onSlotClick')

    def as_setSeasonsDataS(self, data):
        return self.flashObject.as_setSeasonsData(data) if self._isDAAPIInited() else None

    def as_setSlotsDataS(self, data):
        return self.flashObject.as_setSlotsData(data) if self._isDAAPIInited() else None
