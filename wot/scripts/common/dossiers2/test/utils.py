# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/test/utils.py
# Compiled at: 2013-08-29 18:19:37


def getVehicleNationID(vehTypeCompDescr):
    return vehTypeCompDescr >> 4 & 15


def isVehicleSPG(vehTypeCompDescr):
    return False


def getInBattleSeriesIndex(seriesName):
    return {'sniper': 0,
     'killing': 1,
     'piercing': 2}[seriesName]
