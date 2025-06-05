# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/__init__.py
# Compiled at: 2014-11-04 04:28:04
import BigWorld
from debug_utils import LOG_DEBUG
from gui.server_events.EventsCache import g_eventsCache

def isPotapovQuestEnabled():
    try:
        return BigWorld.player().serverSettings['isPotapovQuestEnabled']
    except Exception:
        LOG_DEBUG('There is problem while getting potapov quests supporting flag.Availability value is default')
        return False
