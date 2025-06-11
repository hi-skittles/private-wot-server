# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/ctrl_events.py
# Compiled at: 2014-08-08 04:25:51
import Event

class _PrbCtrlEvents(object):

    def __init__(self):
        super(_PrbCtrlEvents, self).__init__()
        self.__eManager = Event.EventManager()
        self.onPrebattleIntroModeJoined = Event.Event(self.__eManager)
        self.onPrebattleIntroModeLeft = Event.Event(self.__eManager)
        self.onUnitIntroModeLeft = Event.Event(self.__eManager)
        self.onPrebattleInited = Event.Event(self.__eManager)
        self.onUnitIntroModeJoined = Event.Event(self.__eManager)
        self.onUnitIntroModeLeft = Event.Event(self.__eManager)
        self.onPreQueueFunctionalCreated = Event.Event(self.__eManager)
        self.onPreQueueFunctionalDestroyed = Event.Event(self.__eManager)
        self.onPreQueueFunctionalChanged = Event.Event(self.__eManager)

    def clear(self):
        self.__eManager.clear()


g_prbCtrlEvents = _PrbCtrlEvents()
