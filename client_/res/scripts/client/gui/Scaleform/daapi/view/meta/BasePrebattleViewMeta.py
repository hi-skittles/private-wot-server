# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BasePrebattleViewMeta.py
# Compiled at: 2014-07-21 13:30:35
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BasePrebattleViewMeta(DAAPIModule):

    def as_setPyAliasS(self, alias):
        return self.flashObject.as_setPyAlias(alias) if self._isDAAPIInited() else None

    def as_getPyAliasS(self):
        return self.flashObject.as_getPyAlias() if self._isDAAPIInited() else None
