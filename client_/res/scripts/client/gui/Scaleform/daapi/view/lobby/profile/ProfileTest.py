# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTest.py
# Compiled at: 2014-10-01 05:21:17
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.WindowsManager import g_windowsManager
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName

class _ProfileTest(object):

    def __init__(self):
        pass

    def showProfileWindow(self, userName='Happy_3rd_friend'):
        g_windowsManager.window.fireEvent(events.LoadViewEvent(VIEW_ALIAS.PROFILE_WINDOW, getViewName(VIEW_ALIAS.PROFILE_WINDOW, 'test'), {'userName': userName}), EVENT_BUS_SCOPE.LOBBY)


g_instance = _ProfileTest()
