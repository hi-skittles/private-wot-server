# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/EventLogManagerMeta.py
# Compiled at: 2014-04-08 05:16:42
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class EventLogManagerMeta(DAAPIModule):

    def logEvent(self, subSystemType, eventType, uiid, arg):
        self._printOverrideError('logEvent')
