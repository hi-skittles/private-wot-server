# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/ArenaLoadController.py
# Compiled at: 2015-03-24 08:12:31
import BigWorld
from gui import game_control
from gui.battle_control.arena_info import IArenaController
import BattleReplay

class ArenaLoadController(IArenaController):

    def setBattleCtx(self, battleCtx):
        pass

    def spaceLoadStarted(self):
        game_control.g_instance.gameSession.incBattlesCounter()
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.showBattleLoading()
        BigWorld.wg_setReducedFpsMode(True)

    def spaceLoadCompleted(self):
        BigWorld.player().onSpaceLoaded()

    def arenaLoadCompleted(self):
        BigWorld.wg_setReducedFpsMode(False)
        from messenger import MessengerEntry
        MessengerEntry.g_instance.onAvatarShowGUI()
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.showBattle()
        BigWorld.wg_clearTextureReuseList()
        if BattleReplay.isPlaying:
            BattleReplay.g_replayCtrl.onArenaLoaded()
