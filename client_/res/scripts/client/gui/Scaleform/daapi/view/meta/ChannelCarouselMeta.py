# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ChannelCarouselMeta.py
# Compiled at: 2014-11-03 05:40:57
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ChannelCarouselMeta(DAAPIModule):

    def channelOpenClick(self, itemID):
        self._printOverrideError('channelOpenClick')

    def closeAll(self):
        self._printOverrideError('closeAll')

    def channelCloseClick(self, itemID):
        self._printOverrideError('channelCloseClick')

    def as_getDataProviderS(self):
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_getBattlesDataProviderS(self):
        return self.flashObject.as_getBattlesDataProvider() if self._isDAAPIInited() else None
