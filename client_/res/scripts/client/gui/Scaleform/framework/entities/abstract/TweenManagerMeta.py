# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/TweenManagerMeta.py
# Compiled at: 2014-08-08 06:24:14
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TweenManagerMeta(DAAPIModule):

    def createTween(self, tween):
        self._printOverrideError('createTween')

    def disposeTween(self, tween):
        self._printOverrideError('disposeTween')

    def disposeAll(self):
        self._printOverrideError('disposeAll')

    def as_setDataFromXmlS(self, data):
        return self.flashObject.as_setDataFromXml(data) if self._isDAAPIInited() else None
