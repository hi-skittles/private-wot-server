# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/LoaderManagerMeta.py
# Compiled at: 2014-10-31 07:53:41
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LoaderManagerMeta(DAAPIModule):

    def viewLoaded(self, name, view):
        self._printOverrideError('viewLoaded')

    def viewLoadError(self, alias, name, text):
        self._printOverrideError('viewLoadError')

    def viewInitializationError(self, config, alias, name):
        self._printOverrideError('viewInitializationError')

    def as_loadViewS(self, config, alias, name):
        return self.flashObject.as_loadView(config, alias, name) if self._isDAAPIInited() else None
