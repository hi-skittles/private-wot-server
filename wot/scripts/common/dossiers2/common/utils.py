# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/common/utils.py
# Compiled at: 2013-09-23 06:19:54
import struct

def getDossierVersion(dossierCompDescr, versionFormat, latestVersion):
    return latestVersion if dossierCompDescr == '' else struct.unpack_from(versionFormat, dossierCompDescr)[0]
