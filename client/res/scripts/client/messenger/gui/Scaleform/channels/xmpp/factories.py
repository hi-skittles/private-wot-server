# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/xmpp/factories.py
# Compiled at: 2014-12-09 05:26:21
from messenger.gui.Scaleform.channels.xmpp import lobby_controllers
from messenger.gui.interfaces import IControllerFactory
from messenger.proto.xmpp import find_criteria
from messenger.proto.xmpp.gloox_constants import MESSAGE_TYPE
from messenger.storage import storage_getter

class LobbyControllersFactory(IControllerFactory):

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    def init(self):
        controllers = []
        channels = self.channelsStorage.getChannelsByCriteria(find_criteria.XMPPChannelFindCriteria())
        for channel in channels:
            controller = self.factory(channel)
            if controller is not None:
                controllers.append(controller)

        return controllers

    def factory(self, channel):
        controller = None
        msgType = channel.getProtoData().msgType
        if msgType == MESSAGE_TYPE.CHAT:
            controller = lobby_controllers.ChatChannelController(channel)
        return controller
