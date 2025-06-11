# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationLayoutView.py
# Compiled at: 2014-01-28 14:37:18
from notification.BaseNotificationView import BaseNotificationView

class NotificationLayoutView(BaseNotificationView):

    def __init__(self, model=None):
        super(NotificationLayoutView, self).__init__(model)

    def setModel(self, value):
        if self._model is not None:
            self._model.onLayoutSettingsChanged -= self._onLayoutSettingsChanged
        BaseNotificationView.setModel(self, value)
        if self._model is not None:
            self._model.onLayoutSettingsChanged += self._onLayoutSettingsChanged
        return

    def _onLayoutSettingsChanged(self, settings):
        pass

    def cleanUp(self):
        self._model.onLayoutSettingsChanged -= self._onLayoutSettingsChanged
        self.model = None
        return
