# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortCreateDirectionWindowMeta.py
# Compiled at: 2014-01-31 13:15:23
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortCreateDirectionWindowMeta(DAAPIModule):

    def openNewDirection(self):
        self._printOverrideError('openNewDirection')

    def closeDirection(self, id):
        self._printOverrideError('closeDirection')

    def as_setDescriptionS(self, value):
        return self.flashObject.as_setDescription(value) if self._isDAAPIInited() else None

    def as_setupButtonS(self, enabled, visible, ttHeader, ttDescr):
        return self.flashObject.as_setupButton(enabled, visible, ttHeader, ttDescr) if self._isDAAPIInited() else None

    def as_setDirectionsS(self, data):
        return self.flashObject.as_setDirections(data) if self._isDAAPIInited() else None
