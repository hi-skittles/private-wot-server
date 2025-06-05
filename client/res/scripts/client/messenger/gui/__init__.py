# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/__init__.py
# Compiled at: 2013-07-28 12:08:50
from messenger.m_constants import MESSENGER_SCOPE

def setGUIEntries(decorator):
    from messenger.gui.Scaleform.LobbyEntry import LobbyEntry
    from messenger.gui.Scaleform.BattleEntry import BattleEntry
    decorator.setEntry(MESSENGER_SCOPE.LOBBY, LobbyEntry())
    decorator.setEntry(MESSENGER_SCOPE.BATTLE, BattleEntry())
