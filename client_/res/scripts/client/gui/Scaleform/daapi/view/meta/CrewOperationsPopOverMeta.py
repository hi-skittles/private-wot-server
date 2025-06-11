# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrewOperationsPopOverMeta.py
# Compiled at: 2013-12-18 07:25:03
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class CrewOperationsPopOverMeta(DAAPIModule):

    def invokeOperation(self, operationName):
        self._printOverrideError('invokeOperation')

    def as_updateS(self, data):
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None
