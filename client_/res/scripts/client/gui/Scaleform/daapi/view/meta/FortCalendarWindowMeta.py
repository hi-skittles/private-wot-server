# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortCalendarWindowMeta.py
# Compiled at: 2014-06-09 13:41:47
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortCalendarWindowMeta(DAAPIModule):

    def as_updatePreviewDataS(self, data):
        return self.flashObject.as_updatePreviewData(data) if self._isDAAPIInited() else None
