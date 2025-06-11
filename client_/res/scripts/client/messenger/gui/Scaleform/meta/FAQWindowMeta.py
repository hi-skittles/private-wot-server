# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/FAQWindowMeta.py
# Compiled at: 2014-03-19 10:26:01
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FAQWindowMeta(DAAPIModule):

    def onLinkClicked(self, name):
        self._printOverrideError('onLinkClicked')

    def as_appendTextS(self, text):
        return self.flashObject.as_appendText(text) if self._isDAAPIInited() else None
