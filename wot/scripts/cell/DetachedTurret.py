import BigWorld

class DetachedTurret( BigWorld.Entity ):
    def __init__( self ):
        BigWorld.Entity.__init__( self )

    def receiveShot(self, ATTACKER_INFO, SHOT_ID, INT32, VECTOR3, VECTOR3_2, VECTOR3_3):
        pass

    def receiveExplosion(self, VECTOR3, FLOAT32, FLOAT32_2, UINT8):
        pass

    def applyForceToCOM(self, VECTOR3):
        pass
