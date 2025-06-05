# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestRecruitWindowMeta.py
# Compiled at: 2014-10-17 03:57:04
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestRecruitWindowMeta(DAAPIModule):

    def onApply(self, data):
        self._printOverrideError('onApply')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None
