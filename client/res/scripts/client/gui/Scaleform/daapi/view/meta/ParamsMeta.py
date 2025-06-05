# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ParamsMeta.py
# Compiled at: 2014-06-13 12:42:27
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ParamsMeta(DAAPIModule):

    def as_setValuesS(self, data):
        return self.flashObject.as_setValues(data) if self._isDAAPIInited() else None

    def as_highlightParamsS(self, type):
        return self.flashObject.as_highlightParams(type) if self._isDAAPIInited() else None
