# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreTableMeta.py
# Compiled at: 2013-10-18 05:51:43
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class StoreTableMeta(DAAPIModule):

    def refreshStoreTableDataProvider(self):
        self._printOverrideError('refreshStoreTableDataProvider')

    def as_getTableDataProviderS(self):
        return self.flashObject.as_getTableDataProvider() if self._isDAAPIInited() else None

    def as_setTableTypeS(self, type):
        return self.flashObject.as_setTableType(type) if self._isDAAPIInited() else None

    def as_scrollToFirstS(self, level, disabled, currency):
        return self.flashObject.as_scrollToFirst(level, disabled, currency) if self._isDAAPIInited() else None

    def as_setGoldS(self, gold):
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_setCreditsS(self, credits):
        return self.flashObject.as_setCredits(credits) if self._isDAAPIInited() else None
