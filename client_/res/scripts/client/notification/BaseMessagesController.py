# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/BaseMessagesController.py
# Compiled at: 2013-07-28 12:08:50


class BaseMessagesController:

    def __init__(self, model):
        self._model = model

    def cleanUp(self):
        self._model = None
        return
