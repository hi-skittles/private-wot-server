# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationStaffViewMeta.py
# Compiled at: 2015-01-28 06:55:35
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class StaticFormationStaffViewMeta(DAAPIModule):

    def showRecriutmentWindow(self):
        self._printOverrideError('showRecriutmentWindow')

    def showInviteWindow(self):
        self._printOverrideError('showInviteWindow')

    def setRecruitmentOpened(self, opened):
        self._printOverrideError('setRecruitmentOpened')

    def removeMember(self, id, userName):
        self._printOverrideError('removeMember')

    def assignOfficer(self, id, userName):
        self._printOverrideError('assignOfficer')

    def assignPrivate(self, id, userName):
        self._printOverrideError('assignPrivate')

    def as_setStaticHeaderDataS(self, data):
        return self.flashObject.as_setStaticHeaderData(data) if self._isDAAPIInited() else None

    def as_updateHeaderDataS(self, data):
        return self.flashObject.as_updateHeaderData(data) if self._isDAAPIInited() else None

    def as_updateStaffDataS(self, data):
        return self.flashObject.as_updateStaffData(data) if self._isDAAPIInited() else None

    def as_setRecruitmentAvailabilityS(self, available):
        return self.flashObject.as_setRecruitmentAvailability(available) if self._isDAAPIInited() else None
