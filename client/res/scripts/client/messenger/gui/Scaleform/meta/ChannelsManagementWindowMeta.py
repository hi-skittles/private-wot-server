# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ChannelsManagementWindowMeta.py
# Compiled at: 2013-07-28 12:08:50
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ChannelsManagementWindowMeta(DAAPIModule):

    def getSearchLimitLabel(self):
        self._printOverrideError('getSearchLimitLabel')

    def searchToken(self, token):
        self._printOverrideError('searchToken')

    def joinToChannel(self, index):
        self._printOverrideError('joinToChannel')

    def createChannel(self, name, usePassword, password, retype):
        self._printOverrideError('createChannel')

    def as_freezSearchButtonS(self, isEnable):
        return self.flashObject.as_freezSearchButton(isEnable) if self._isDAAPIInited() else None

    def as_getDataProviderS(self):
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None
