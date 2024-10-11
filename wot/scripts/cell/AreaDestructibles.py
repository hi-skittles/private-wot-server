import BigWorld

class AreaDestructibles( BigWorld.Entity ):
    def __init__( self ):
        BigWorld.Entity.__init__( self )

    def reset(self):
        pass

    def addArtilleryPreparation(self, ATTACKER_INFO, UINT16, VECTOR3, VECTOR3_2, TUPLE, TUPLE_2, FLOAT32, FLOAT32_2, FLOAT32_3, TUPLE_3, TUPLE_4, TUPLE_5, INT32, TUPLE_6, FLOAT64):
        # TUPLE is a list of FLOAT32
        # TUPLE_2 is a list of FLOAT32
        # TUPLE_3 is a list of FLOAT32
        # TUPLE_4 is a list of FLOAT32
        # TUPLE_5 is a list of UINT16
        # TUPLE_6 is a list of FLOAT32
        pass

    def addArtillery(self, ATTACKER_INFO, UINT16, VECTOR3, VECTOR3_2, TUPLE, TUPLE_2, FLOAT32, FLOAT32_2, FLOAT32_3, FLOAT32_4, FLOAT32_5, UINT16_2, FLOAT32_6, INT32, TUPLE_3, FLOAT64):
        # TUPLE is a list of FLOAT32
        # TUPLE_2 is a list of FLOAT32
        # TUPLE_3 is a list of FLOAT32
        pass

    def addBomber(self, ATTACKER_INFO, UINT16, VECTOR3, VECTOR2, TUPLE, TUPLE_2, FLOAT32, UINT16_2, TUPLE_3, FLOAT32_2, FLOAT32_3, ARRAY, ARRAY_2, ARRAY_3, FLOAT32_4, UINT16_3, INT32, UINT8, TUPLE_4, FLOAT32_5, FLOAT64):
        # TUPLE_ is a list of VECTOR2
        # TUPLE_2 is a list of VECTOR2
        # TUPLE_3 is a list of FLOAT32
        # ARRAY is a list of FLOAT32
        # ARRAY_2 is a list of FLOAT32
        # ARRAY_3 is a list of BOOL
        # TUPLE_4 is a list of FLOAT32
        pass

    def takeOverProjectile(self, ATTACKER_INFO, SHOT_ID, INT32, UINT8, UINT8_2, ARRAY, TUPLE, FLOAT32, FLOAT64, VECTOR3, VECTOR3_2, FLOAT32_2, FLOAT32_3, FLOAT32_4, FLOAT64_2):
        # ARRAY is a list of OBJECT_ID
        # TUPLE is a list of FLOAT32
        pass

    def damageDestructibleAndTakeOverProjectile(self, UINT8, UINT8_2, FLOAT32, VECTOR3, VECTOR3_2, ATTACKER_INFO, SHOT_ID, INT32, UINT8_3, UINT8_4, ARRAY, TUPLE, FLOAT32_2, FLOAT64, VECTOR3_3, VECTOR3_4, FLOAT32_3, FLOAT32_4, FLOAT32_5, FLOAT64_2):
        # ARRAY is a list of OBJECT_ID
        # TUPLE is a list of FLOAT32
        pass

    def damageDestructible(self, UINT8, UINT8_2, FLOAT32, FLOAT32_2, FLOAT32_3, INT8, DESTRUCTIBLE_ATTACK_INFO):
        pass

    def receiveMiss(self, SHOT_ID, UINT16):
        pass

    def receiveAttackResults(self, ATTACK_RESULTS):
        pass

    def receiveTaggedDestructibleKill(self, UINT8):
        pass
