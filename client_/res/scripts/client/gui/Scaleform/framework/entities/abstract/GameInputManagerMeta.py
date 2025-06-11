# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/GameInputManagerMeta.py
# Compiled at: 2013-10-16 07:19:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class GameInputManagerMeta(DAAPIModule):

    def handleGlobalKeyEvent(self, keyCode, eventType):
        self._printOverrideError('handleGlobalKeyEvent')

    def as_addKeyHandlerS(self, keyCode, eventType, ignoreText, cancelEventType):
        return self.flashObject.as_addKeyHandler(keyCode, eventType, ignoreText, cancelEventType) if self._isDAAPIInited() else None

    def as_clearKeyHandlerS(self, keyCode, eventType):
        return self.flashObject.as_clearKeyHandler(keyCode, eventType) if self._isDAAPIInited() else None
