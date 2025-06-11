# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RallyBaseViewMeta.py
# Compiled at: 2014-02-25 05:53:27
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class RallyBaseViewMeta(DAAPIModule):

    def as_setPyAliasS(self, alias):
        return self.flashObject.as_setPyAlias(alias) if self._isDAAPIInited() else None

    def as_getPyAliasS(self):
        return self.flashObject.as_getPyAlias() if self._isDAAPIInited() else None
