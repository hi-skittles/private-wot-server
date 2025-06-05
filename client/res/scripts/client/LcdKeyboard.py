# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LcdKeyboard.py
# Compiled at: 2010-11-10 10:12:53
import BigWorld
_g_instance = None

class LCD_KEY:
    LEFT = 256
    RIGHT = 512
    OK = 1024
    CANCEL = 2048
    UP = 4096
    DOWN = 8192
    MENU = 16384


def enableLcdKeyboardSpecificKeys(bValue):
    global _g_instance
    if bValue:
        if _g_instance is not None:
            return True
        _g_instance = BigWorld.WGLcdKeyboard()
        if not _g_instance.isValid():
            _g_instance.destroy()
            _g_instance = None
            return False
    else:
        if _g_instance is None:
            return True
        _g_instance.destroy()
        _g_instance = None
    return True


def getKeys(mask=4294967295L):
    return 0 if _g_instance is None else _g_instance.getKeys() & mask


def finalize():
    enableLcdKeyboardSpecificKeys(False)
