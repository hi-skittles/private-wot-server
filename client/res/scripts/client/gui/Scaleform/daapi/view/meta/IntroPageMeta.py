# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IntroPageMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class IntroPageMeta(DAAPIModule):

    def stopVideo(self):
        self._printOverrideError('stopVideo')

    def handleError(self, data):
        self._printOverrideError('handleError')

    def as_playVideoS(self, data):
        return self.flashObject.as_playVideo(data) if self._isDAAPIInited() else None
