# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/parsers/Parser.py
# Compiled at: 2014-09-23 06:37:47


class Parser(object):

    @staticmethod
    def parseVehicles(data):
        return data

    @staticmethod
    def parseModules(data, type):
        return data

    @staticmethod
    def getParser(itemTypeID):
        return Parser.parseVehicles if itemTypeID == 1 else (lambda data: Parser.parseModules(data, itemTypeID))
