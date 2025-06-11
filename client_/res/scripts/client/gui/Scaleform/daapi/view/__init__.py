# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/__init__.py
# Compiled at: 2014-11-25 11:30:19
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.APPEAL_USER, 'gui.Scaleform.daapi.view.lobby.user_cm_handlers', 'AppealCMHandler')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.BASE_USER, 'gui.Scaleform.daapi.view.lobby.user_cm_handlers', 'BaseUserCMHandler')
