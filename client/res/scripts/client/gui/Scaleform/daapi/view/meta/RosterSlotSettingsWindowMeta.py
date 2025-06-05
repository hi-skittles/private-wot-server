# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RosterSlotSettingsWindowMeta.py
# Compiled at: 2014-02-06 03:05:27
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class RosterSlotSettingsWindowMeta(DAAPIModule):

    def onFiltersUpdate(self, nation, vehicleType, isMain, level, compatibleOnly):
        self._printOverrideError('onFiltersUpdate')

    def getFilterData(self):
        self._printOverrideError('getFilterData')

    def submitButtonHandler(self, value):
        self._printOverrideError('submitButtonHandler')

    def cancelButtonHandler(self):
        self._printOverrideError('cancelButtonHandler')

    def as_setDefaultDataS(self, value):
        return self.flashObject.as_setDefaultData(value) if self._isDAAPIInited() else None

    def as_setListDataS(self, listData):
        return self.flashObject.as_setListData(listData) if self._isDAAPIInited() else None
