# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/PlayerBonusesPanel.py
# Compiled at: 2010-04-16 10:54:14
import BigWorld
from gui import DebugMonitorView
from gui import DEPTH_OF_PlayerBonusesPanel
import constants
from debug_utils import *

class PlayerBonusesPanel(object):

    def __init__(self):
        self.__monitor = None
        return

    def prerequisites(self):
        return []

    def start(self):
        self.__monitor = self.__createDebugMonitorView()

    def destroy(self):
        self.__monitor.destroy()
        self.__monitor = None
        return

    def setVisible(self, bValue):
        if self.__monitor is not None:
            self.__monitor.setVisible(bValue)
        return

    def getVisible(self):
        return self.__monitor.getVisible() if self.__monitor is not None else False

    def setContent(self, content):
        self.__monitor.setContent(content)

    def __createDebugMonitorView(self):
        result = DebugMonitorView.DebugMonitorView()
        result.setPosition((-0.99, 0.15, DEPTH_OF_PlayerBonusesPanel))
        result.setAlign((True,
         True,
         True,
         True))
        result.setMargin((0.04, 0.04, 0.04, 0.04))
        result.setVisible(True)
        return result
