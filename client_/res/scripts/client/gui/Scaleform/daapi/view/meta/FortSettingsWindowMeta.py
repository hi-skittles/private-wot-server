# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortSettingsWindowMeta.py
# Compiled at: 2014-10-17 11:47:24
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortSettingsWindowMeta(DAAPIModule):

    def activateDefencePeriod(self):
        self._printOverrideError('activateDefencePeriod')

    def disableDefencePeriod(self):
        self._printOverrideError('disableDefencePeriod')

    def cancelDisableDefencePeriod(self):
        self._printOverrideError('cancelDisableDefencePeriod')

    def as_setFortClanInfoS(self, data):
        return self.flashObject.as_setFortClanInfo(data) if self._isDAAPIInited() else None

    def as_setMainStatusS(self, title, msg, toolTip):
        return self.flashObject.as_setMainStatus(title, msg, toolTip) if self._isDAAPIInited() else None

    def as_setViewS(self, value):
        return self.flashObject.as_setView(value) if self._isDAAPIInited() else None

    def as_setDataForActivatedS(self, data):
        return self.flashObject.as_setDataForActivated(data) if self._isDAAPIInited() else None

    def as_setCanDisableDefencePeriodS(self, value):
        return self.flashObject.as_setCanDisableDefencePeriod(value) if self._isDAAPIInited() else None

    def as_setDataForNotActivatedS(self, data):
        return self.flashObject.as_setDataForNotActivated(data) if self._isDAAPIInited() else None
