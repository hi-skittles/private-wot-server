# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/migration/MigrationServerSettings.py
# Compiled at: 2014-10-17 09:47:23
from messenger.proto.interfaces import IProtoSettings

class MigrationServerSettings(IProtoSettings):

    def __init__(self):
        super(MigrationServerSettings, self).__init__()

    def isEnabled(self):
        return True
