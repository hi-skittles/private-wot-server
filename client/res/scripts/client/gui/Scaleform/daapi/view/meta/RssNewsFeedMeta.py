# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RssNewsFeedMeta.py
# Compiled at: 2014-04-22 08:24:20
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class RssNewsFeedMeta(DAAPIModule):

    def openBrowser(self, linkToOpen):
        self._printOverrideError('openBrowser')

    def as_updateFeedS(self, feed):
        return self.flashObject.as_updateFeed(feed) if self._isDAAPIInited() else None
