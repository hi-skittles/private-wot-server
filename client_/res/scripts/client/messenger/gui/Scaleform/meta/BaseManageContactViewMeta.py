# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/BaseManageContactViewMeta.py
# Compiled at: 2014-12-03 04:33:11
from messenger.gui.Scaleform.view.BaseContactView import BaseContactView

class BaseManageContactViewMeta(BaseContactView):

    def checkText(self, txt):
        self._printOverrideError('checkText')

    def as_setLabelS(self, msg):
        return self.flashObject.as_setLabel(msg) if self._isDAAPIInited() else None

    def as_setInputTextS(self, msg):
        return self.flashObject.as_setInputText(msg) if self._isDAAPIInited() else None
