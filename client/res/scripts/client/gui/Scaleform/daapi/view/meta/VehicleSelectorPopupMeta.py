# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSelectorPopupMeta.py
# Compiled at: 2014-12-24 08:54:08
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class VehicleSelectorPopupMeta(DAAPIModule):

    def onFiltersUpdate(self, nation, vehicleType, isMain, level, compatibleOnly):
        self._printOverrideError('onFiltersUpdate')

    def onSelectVehicles(self, items):
        self._printOverrideError('onSelectVehicles')

    def as_setFiltersDataS(self, data):
        return self.flashObject.as_setFiltersData(data) if self._isDAAPIInited() else None

    def as_setListDataS(self, listData, selectedItems):
        return self.flashObject.as_setListData(listData, selectedItems) if self._isDAAPIInited() else None

    def as_setListModeS(self, isMultipleSelect):
        return self.flashObject.as_setListMode(isMultipleSelect) if self._isDAAPIInited() else None

    def as_setInfoTextS(self, text, componentsOffset):
        return self.flashObject.as_setInfoText(text, componentsOffset) if self._isDAAPIInited() else None
