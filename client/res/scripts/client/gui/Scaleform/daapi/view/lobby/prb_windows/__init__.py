# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/__init__.py
# Compiled at: 2014-11-25 11:30:19
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
__all___ = ('PrbSendInvitesWindow', 'SquadWindow', 'BattleSessionWindow', 'BattleSessionList')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.PREBATTLE_USER, 'gui.Scaleform.daapi.view.lobby.prb_windows.PrebattleUserCMHandler', 'PrebattleUserCMHandler')
