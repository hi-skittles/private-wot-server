# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortWelcomeViewMeta.py
# Compiled at: 2014-12-05 08:34:00
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortWelcomeViewMeta(DAAPIModule):

    def onViewReady(self):
        self._printOverrideError('onViewReady')

    def onCreateBtnClick(self):
        self._printOverrideError('onCreateBtnClick')

    def onNavigate(self, code):
        self._printOverrideError('onNavigate')

    def as_setWarningTextS(self, text, disabledBtnTooltipHeader, disabledBtnTooltipBody):
        return self.flashObject.as_setWarningText(text, disabledBtnTooltipHeader, disabledBtnTooltipBody) if self._isDAAPIInited() else None

    def as_setHyperLinksS(self, searchClanLink, createClanLink, detailLink):
        return self.flashObject.as_setHyperLinks(searchClanLink, createClanLink, detailLink) if self._isDAAPIInited() else None

    def as_setCommonDataS(self, data):
        return self.flashObject.as_setCommonData(data) if self._isDAAPIInited() else None

    def as_setRequirementTextS(self, text):
        return self.flashObject.as_setRequirementText(text) if self._isDAAPIInited() else None
