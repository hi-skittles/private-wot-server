# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AbstractRallyViewMeta.py
# Compiled at: 2014-07-21 13:42:11
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class AbstractRallyViewMeta(DAAPIModule):

    def as_setPyAliasS(self, alias):
        return self.flashObject.as_setPyAlias(alias) if self._isDAAPIInited() else None

    def as_getPyAliasS(self):
        return self.flashObject.as_getPyAlias() if self._isDAAPIInited() else None
