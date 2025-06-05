# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ContainerManagerMeta.py
# Compiled at: 2014-10-31 07:53:41
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ContainerManagerMeta(DAAPIModule):

    def isModalViewsIsExists(self):
        self._printOverrideError('isModalViewsIsExists')

    def canCancelPreviousLoading(self, containerType):
        self._printOverrideError('canCancelPreviousLoading')

    def as_getViewS(self, name):
        return self.flashObject.as_getView(name) if self._isDAAPIInited() else None

    def as_showS(self, name, x, y):
        return self.flashObject.as_show(name, x, y) if self._isDAAPIInited() else None

    def as_hideS(self, name):
        return self.flashObject.as_hide(name) if self._isDAAPIInited() else None

    def as_registerContainerS(self, type, name):
        return self.flashObject.as_registerContainer(type, name) if self._isDAAPIInited() else None

    def as_unregisterContainerS(self, type):
        return self.flashObject.as_unregisterContainer(type) if self._isDAAPIInited() else None

    def as_closePopUpsS(self):
        return self.flashObject.as_closePopUps() if self._isDAAPIInited() else None

    def as_isOnTopS(self, cType, vName):
        return self.flashObject.as_isOnTop(cType, vName) if self._isDAAPIInited() else None

    def as_bringToFrontS(self, cType, vName):
        return self.flashObject.as_bringToFront(cType, vName) if self._isDAAPIInited() else None
