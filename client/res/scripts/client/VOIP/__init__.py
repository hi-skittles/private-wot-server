# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VOIP/__init__.py
# Compiled at: 2014-11-12 10:25:50
import BigWorld
from VOIPManager import VOIPManager

def getVOIPManager():
    if not globals().has_key('__handler'):
        globals()['__handler'] = VOIPManager()
        BigWorld.VOIP.setHandler(__handler)
    return __handler
