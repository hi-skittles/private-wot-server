import BigWorld

class Vehicle(BigWorld.Entity):
    def __init__(self):
        BigWorld.Entity.__init__(self)

    def moveWith(self, UINT8):
        # Exposed tag
        pass

    def trackPointWithGun(self, VECTOR3):
        # Exposed tag
        pass

    def stopTrackingWithGun(self, FLOAT32, FLOAT32_2):
        # Exposed tag
        pass

    def trackVehicleWithGun(self, OBJECT_ID):
        pass

    def changeSetting(self, UINT8, INT32):
        # Exposed tag
        pass

    def sendVisibilityDevelopmentInfo(self, OBJECT_ID, VECTOR3):
        # Exposed tag
        pass

    def shoot(self, FLOAT32):
        pass

    def setEquipmentApplicationPoint(self, UINT16, VECTOR3, VECTOR2):
        pass

    def useHorn(self, BOOL):
        pass

    def teleportTo(self, VECTOR3, FLOAT32):
        pass

    def replenishAmmo(self):
        pass

    def setDevelopmentFeature(self, STRING, INT32):
        pass

    def receiveFakeShot(self, INT32, FLOAT32, VECTOR3, VECTOR3_2, UINT8):
        pass

    def setAvatar(self, MAILBOX):
        pass

    def registerObserver(self, MAILBOX, BOOL):
        pass

    def sendFinalStats(self, PYTHON):
        pass

    def onClientConnected(self, BOOL):
        pass

    def onBattleRunning(self, BOOL):
        pass

    def receiveShot(self, ATTACKER_INFO, SHOT_ID, INT32, UINT8, FLOAT32, VECTOR3, VECTOR3_2, TUPLE, TUPLE_2, FLOAT32_2, TUPLE_3):
        # TUPLE is a list of FLOAT32
        # TUPLE_2 is a list of TUPLE and each TUPLE is a list of FLOAT32
        # TUPLE_3 is a list of FLOAT32
        pass

    def receiveExplosion(self, ATTACKER_INFO, SHOT_ID, INT32, VECTOR3, FLOAT32, FLOAT32_2, FLOAT32_3, UINT8):
        pass

    def receiveRamming(self, OBJECT_ID, UINT8, FLOAT32, FLOAT32_2, UINT8_2, FLOAT32_3, FLOAT32_4, FLOAT32_5, BOOL):
        pass

    def receivePressure(self, BOOL, BOOL_2, OBJECT_ID, FLOAT32):
        pass

    def receiveMiss(self, SHOT_ID, UINT16):
        pass

    def receiveAttackResults(self, ATTACK_RESULTS):
        pass

    def receiveHitAssistBonus(self, OBJECT_ID, INT32, INT32_2, INT32_3, UINT8, UINT8_2, BOOL, UINT16):
        pass

    def onEnemyVehicleShot(self, OBJECT_ID, ARRAY, UINT8, FLOAT32, FLOAT32_2):
        # ARRAY is a list of SHOT_ID
        pass

    def onEnemyVehicleBecameMovingOrStill(self, OBJECT_ID, FLOAT32):
        pass

    def onTeamBaseCaptured(self, FLOAT32, BOOL):
        pass

    def onObservedByEnemy(self, OBJECT_ID, BOOL):
        pass

    def onStopObservationByEnemy(self, OBJECT_ID):
        pass

    def onCombatEquipmentShootingStarted(self, UINT16, VECTOR3, FLOAT32, TUPLE):
        # TUPLE is a list of INT32
        pass

    def receiveAssistsFromArena(self, ARRAY, ARRAY_2):
        # ARRAY is a list of UINT8
        # ARRAY_2 is a list of OBJECT_ID
        pass

    def receiveFirstDetectionsFromArena(self, ARRAY, ARRAY_2):
        # ARRAY is a list of OBJECT_ID
        # ARRAY_2 is a list of OBJECT_ID
        pass

    def receiveTeamBasePoints(self, FLOAT32):
        pass

    def sendPositionsToClient(self, BOOL):
        pass

    def onRammedByAlly(self):
        pass

    def requestDamagedDevicesFromFor(self, OBJECT_ID, MAILBOX):
        pass

    def sendDamagedDevicesTo(self, MAILBOX):
        pass

    def setHonorTitle(self, STRING):
        pass

    def receiveTaggedDestructibleKill(self, UINT8):
        pass

    def setOnFireByExplosion(self, ATTACKER_INFO, SHOT_ID):
        pass

    def receiveVisibilityInfo(self, ARRAY, ARRAY_2, ARRAY_3):
        # ARRAY is a list of OBJECT_ID
        # ARRAY_2 is a list of FLOAT32
        # ARRAY_3 is a list of FLOAT32
        pass

    def onTrackAssist(self):
        pass
