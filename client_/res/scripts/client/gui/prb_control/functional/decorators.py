# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/functional/decorators.py
# Compiled at: 2014-01-28 10:33:29
from adisp import process
from gui.shared.utils.functions import checkAmmoLevel

def vehicleAmmoCheck(func):

    @process
    def wrapper(*args, **kwargs):
        res = yield checkAmmoLevel()
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper
