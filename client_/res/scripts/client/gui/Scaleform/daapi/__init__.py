# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/__init__.py
# Compiled at: 2014-11-25 11:30:19
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View

class LobbySubView(View, AppRef):

    def __init__(self, backAlpha=0.6):
        super(LobbySubView, self).__init__()
        self.gfx.backgroundAlpha = backAlpha
