# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileAchievementSectionMeta.py
# Compiled at: 2015-01-08 09:14:28
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileAchievementSectionMeta(DAAPIModule):

    def as_setRareAchievementDataS(self, data):
        return self.flashObject.as_setRareAchievementData(data) if self._isDAAPIInited() else None
