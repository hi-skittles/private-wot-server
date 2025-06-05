# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/fortifications/events_dispatcher.py
# Compiled at: 2015-01-14 08:39:27
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES

def showFortBattleRoomWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)


def showBattleConsumesIntro():
    g_eventBus.handleEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_COMBAT_RESERVES_INTRO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
