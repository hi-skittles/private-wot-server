# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ArtilleryEquipment.py
# Compiled at: 2014-12-31 06:29:20
from AvatarInputHandler import mathUtils
import BigWorld
from Math import Vector3

class ArtilleryEquipment(BigWorld.UserDataObject):

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        launchDir = mathUtils.createRotationMatrix((self.__dict__['yaw'], self.__dict__['pitch'], 0)).applyToAxis(2)
        launchDir.normalise()
        self.launchVelocity = launchDir * self.speed
