# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/__init__.py
# Compiled at: 2013-07-28 12:08:50
from items import _xml

def readDict(xmlCtx, section, subsectionName, converter=lambda value: value.asString):
    result = {}
    for name, value in _xml.getChildren(xmlCtx, section, subsectionName):
        result[name] = converter(value)

    return result
