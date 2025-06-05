# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AreaTrigger.py
# Compiled at: 2012-10-02 10:12:44
import BigWorld
import TriggersManager

class AreaTrigger(BigWorld.UserDataObject):

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        self.__id = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.AREA, name=self.name, position=self.position, radius=self.radius, exitInterval=self.exitInterval)

    def destroy(self):
        TriggersManager.g_manager.delTrigger(self.__id)
