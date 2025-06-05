# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReferralReferralsIntroWindowMeta.py
# Compiled at: 2014-09-10 10:45:22
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ReferralReferralsIntroWindowMeta(DAAPIModule):

    def onClickApplyBtn(self):
        self._printOverrideError('onClickApplyBtn')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
