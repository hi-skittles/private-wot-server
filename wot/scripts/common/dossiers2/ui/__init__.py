# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/ui/__init__.py
# Compiled at: 2014-07-11 07:32:39
from dossiers2.ui.layouts import init as ui_layouts_init
from dossiers2.ui.achievements import init as achieves_init

def init():
    achieves_init('scripts/item_defs/achievements.xml')
    ui_layouts_init()
