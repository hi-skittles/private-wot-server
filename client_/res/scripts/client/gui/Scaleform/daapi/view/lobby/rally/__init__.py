# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/__init__.py
# Compiled at: 2014-11-25 11:30:19
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
__author__ = 'd_dichkovsky'
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.UNIT_USER, 'gui.Scaleform.daapi.view.lobby.rally.UnitUserCMHandler', 'UnitUserCMHandler')

class NavigationStack(object):
    __stacks = {}

    @classmethod
    def clear(cls, key):
        if key in cls.__stacks:
            cls.__stacks[key] = []

    @classmethod
    def exclude(cls, key, flashAlias):
        items = cls.__stacks.get(key, [])[:]
        for item in items:
            if item[0] == flashAlias:
                cls.__stacks[key].remove(item)

    @classmethod
    def hasHistory(cls, key):
        return len(cls.__stacks[key]) if key in cls.__stacks else 0

    @classmethod
    def current(cls, key):
        return cls.__stacks[key][-1] if key in cls.__stacks and len(cls.__stacks[key]) else None

    @classmethod
    def prev(cls, key):
        return cls.__stacks[key][-2] if key in cls.__stacks and len(cls.__stacks[key]) > 1 else None

    @classmethod
    def nav2Next(cls, key, flashAlias, pyAlias, itemID):
        item = (flashAlias, pyAlias, itemID)
        if key in cls.__stacks:
            if item not in cls.__stacks[key]:
                cls.__stacks[key].append(item)
        else:
            cls.__stacks[key] = [item]

    @classmethod
    def nav2Prev(cls, key):
        return cls.__stacks[key].pop() if key in cls.__stacks and len(cls.__stacks[key]) else None
