# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsWindowMeta.py
# Compiled at: 2014-11-13 07:06:36
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsWindowMeta(DAAPIModule):

    def onTabSelected(self, tabID):
        self._printOverrideError('onTabSelected')

    def as_loadViewS(self, flashAlias, pyAlias):
        return self.flashObject.as_loadView(flashAlias, pyAlias) if self._isDAAPIInited() else None

    def as_selectTabS(self, tabID):
        return self.flashObject.as_selectTab(tabID) if self._isDAAPIInited() else None
