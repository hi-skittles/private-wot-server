# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw/BWServerSettings.py
# Compiled at: 2014-03-06 04:58:29
from messenger.proto.interfaces import IProtoSettings

class BWServerSettings(IProtoSettings):

    def __init__(self):
        super(BWServerSettings, self).__init__()

    def isEnabled(self):
        return True
