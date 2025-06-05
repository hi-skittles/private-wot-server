# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReportBugMeta.py
# Compiled at: 2014-11-20 03:36:42
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ReportBugMeta(DAAPIModule):

    def reportBug(self):
        self._printOverrideError('reportBug')

    def as_setHyperLinkS(self, value):
        return self.flashObject.as_setHyperLink(value) if self._isDAAPIInited() else None
