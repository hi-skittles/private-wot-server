# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDisconnectViewMeta.py
# Compiled at: 2014-05-08 10:26:33
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortDisconnectViewMeta(DAAPIModule):

    def as_setWarningTextsS(self, warningTxt, warningDescTxt):
        return self.flashObject.as_setWarningTexts(warningTxt, warningDescTxt) if self._isDAAPIInited() else None
