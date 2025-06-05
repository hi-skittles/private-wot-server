# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/AbstractWindowView.py
# Compiled at: 2014-10-01 05:21:17
from gui.Scaleform.daapi.view.meta.WindowViewMeta import WindowViewMeta
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class AbstractWindowView(WrapperViewMeta, WindowViewMeta):

    def __init__(self, ctx=None):
        super(AbstractWindowView, self).__init__()

    def onTryClosing(self):
        return True
