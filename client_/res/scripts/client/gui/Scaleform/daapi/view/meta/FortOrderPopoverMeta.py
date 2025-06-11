# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderPopoverMeta.py
# Compiled at: 2014-12-24 08:33:34
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortOrderPopoverMeta(DAAPIModule):

    def requestForCreateOrder(self):
        self._printOverrideError('requestForCreateOrder')

    def requestForUseOrder(self):
        self._printOverrideError('requestForUseOrder')

    def getLeftTime(self):
        self._printOverrideError('getLeftTime')

    def getLeftTimeStr(self):
        self._printOverrideError('getLeftTimeStr')

    def getLeftTimeTooltip(self):
        self._printOverrideError('getLeftTimeTooltip')

    def openQuest(self, questID):
        self._printOverrideError('openQuest')

    def openOrderDetailsWindow(self):
        self._printOverrideError('openOrderDetailsWindow')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_disableOrderS(self, daisable):
        return self.flashObject.as_disableOrder(daisable) if self._isDAAPIInited() else None
