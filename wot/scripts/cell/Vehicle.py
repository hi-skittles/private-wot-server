import BigWorld

from bwdebug import DEBUG_MSG


class Vehicle(BigWorld.Entity):
    def __init__(self):
        BigWorld.Entity.__init__(self)

    def moveWith(self, UINT8):
        # Exposed tag
        DEBUG_MSG("Vehicle::moveWith", UINT8)

    def trackPointWithGun(self, VECTOR3):
        # Exposed tag
        DEBUG_MSG("Vehicle::trackPointWithGun", VECTOR3)

    def stopTrackingWithGun(self, FLOAT32, FLOAT32_2):
        # Exposed tag
        DEBUG_MSG("Vehicle::stopTrackingWithGun", FLOAT32, FLOAT32_2)

    def trackVehicleWithGun(self, OBJECT_ID):
        DEBUG_MSG("Vehicle::trackVehicleWithGun", OBJECT_ID)

    def changeSetting(self, UINT8, INT32):
        # Exposed tag
        DEBUG_MSG("Vehicle::changeSetting", UINT8, INT32)

    def sendVisibilityDevelopmentInfo(self, OBJECT_ID, VECTOR3):
        # Exposed tag
        DEBUG_MSG("Vehicle::sendVisibilityDevelopmentInfo", OBJECT_ID, VECTOR3)

    def shoot(self, FLOAT32):
        DEBUG_MSG("Vehicle::shoot", FLOAT32)

    def setEquipmentApplicationPoint(self, UINT16, VECTOR3, VECTOR2):
        DEBUG_MSG("Vehicle::setEquipmentApplicationPoint", UINT16, VECTOR3, VECTOR2)

    def useHorn(self, BOOL):
        DEBUG_MSG("Vehicle::useHorn", BOOL)

    def teleportTo(self, VECTOR3, FLOAT32):
        DEBUG_MSG("Vehicle::teleportTo", VECTOR3, FLOAT32)

    def replenishAmmo(self):
        DEBUG_MSG("Vehicle::replenishAmmo")

    def setDevelopmentFeature(self, STRING, INT32):
        DEBUG_MSG("Vehicle::setDevelopmentFeature", STRING, INT32)

    def receiveFakeShot(self, INT32, FLOAT32, VECTOR3, VECTOR3_2, UINT8):
        DEBUG_MSG("Vehicle::receiveFakeShot", INT32, FLOAT32, VECTOR3, VECTOR3_2, UINT8)

    def setAvatar(self, MAILBOX):
        DEBUG_MSG("Vehicle::setAvatar", MAILBOX)

    def registerObserver(self, MAILBOX, BOOL):
        DEBUG_MSG("Vehicle::registerObserver", MAILBOX, BOOL)

    def sendFinalStats(self, PYTHON):
        DEBUG_MSG("Vehicle::sendFinalStats", PYTHON)

    def onClientConnected(self, BOOL):
        DEBUG_MSG("Vehicle::onClientConnected", BOOL)

    def onBattleRunning(self, BOOL):
        DEBUG_MSG("Vehicle::onBattleRunning", BOOL)

    def receiveShot(self, ATTACKER_INFO, SHOT_ID, INT32, UINT8, FLOAT32, VECTOR3, VECTOR3_2, TUPLE, TUPLE_2, FLOAT32_2, TUPLE_3):
        # TUPLE is a list of FLOAT32
        # TUPLE_2 is a list of TUPLE and each TUPLE is a list of FLOAT32
        # TUPLE_3 is a list of FLOAT32
        DEBUG_MSG("Vehicle::receiveShot", ATTACKER_INFO, SHOT_ID, INT32, UINT8, FLOAT32, VECTOR3, VECTOR3_2, TUPLE, TUPLE_2, FLOAT32_2, TUPLE_3)

    def receiveExplosion(self, ATTACKER_INFO, SHOT_ID, INT32, VECTOR3, FLOAT32, FLOAT32_2, FLOAT32_3, UINT8):
        DEBUG_MSG("Vehicle::receiveExplosion", ATTACKER_INFO, SHOT_ID, INT32, VECTOR3, FLOAT32, FLOAT32_2, FLOAT32_3, UINT8)

    def receiveRamming(self, OBJECT_ID, UINT8, FLOAT32, FLOAT32_2, UINT8_2, FLOAT32_3, FLOAT32_4, FLOAT32_5, BOOL):
        DEBUG_MSG("Vehicle::receiveRamming", OBJECT_ID, UINT8, FLOAT32, FLOAT32_2, UINT8_2, FLOAT32_3, FLOAT32_4, FLOAT32_5, BOOL)

    def receivePressure(self, BOOL, BOOL_2, OBJECT_ID, FLOAT32):
        DEBUG_MSG("Vehicle::receivePressure", BOOL, BOOL_2, OBJECT_ID, FLOAT32)

    def receiveMiss(self, SHOT_ID, UINT16):
        DEBUG_MSG("Vehicle::receiveMiss", SHOT_ID, UINT16)

    def receiveAttackResults(self, ATTACK_RESULTS):
        DEBUG_MSG("Vehicle::receiveAttackResults", ATTACK_RESULTS)

    def receiveHitAssistBonus(self, OBJECT_ID, INT32, INT32_2, INT32_3, UINT8, UINT8_2, BOOL, UINT16):
        DEBUG_MSG("Vehicle::receiveHitAssistBonus", OBJECT_ID, INT32, INT32_2, INT32_3, UINT8, UINT8_2, BOOL, UINT16)

    def onEnemyVehicleShot(self, OBJECT_ID, ARRAY, UINT8, FLOAT32, FLOAT32_2):
        # ARRAY is a list of SHOT_ID
        DEBUG_MSG("Vehicle::onEnemyVehicleShot", OBJECT_ID, ARRAY, UINT8, FLOAT32, FLOAT32_2)

    def onEnemyVehicleBecameMovingOrStill(self, OBJECT_ID, FLOAT32):
        DEBUG_MSG("Vehicle::onEnemyVehicleBecameMovingOrStill", OBJECT_ID, FLOAT32)

    def onTeamBaseCaptured(self, FLOAT32, BOOL):
        DEBUG_MSG("Vehicle::onTeamBaseCaptured", FLOAT32, BOOL)

    def onObservedByEnemy(self, OBJECT_ID, BOOL):
        DEBUG_MSG("Vehicle::onObservedByEnemy", OBJECT_ID, BOOL)

    def onStopObservationByEnemy(self, OBJECT_ID):
        DEBUG_MSG("Vehicle::onStopObservationByEnemy", OBJECT_ID)

    def onCombatEquipmentShootingStarted(self, UINT16, VECTOR3, FLOAT32, TUPLE):
        # TUPLE is a list of INT32
        DEBUG_MSG("Vehicle::onCombatEquipmentShootingStarted", UINT16, VECTOR3, FLOAT32, TUPLE)

    def receiveAssistsFromArena(self, ARRAY, ARRAY_2):
        # ARRAY is a list of UINT8
        # ARRAY_2 is a list of OBJECT_ID
        DEBUG_MSG("Vehicle::receiveAssistsFromArena", ARRAY, ARRAY_2)

    def receiveFirstDetectionsFromArena(self, ARRAY, ARRAY_2):
        # ARRAY is a list of OBJECT_ID
        # ARRAY_2 is a list of OBJECT_ID
        DEBUG_MSG("Vehicle::receiveFirstDetectionsFromArena", ARRAY, ARRAY_2)

    def receiveTeamBasePoints(self, FLOAT32):
        DEBUG_MSG("Vehicle::receiveTeamBasePoints", FLOAT32)

    def sendPositionsToClient(self, BOOL):
        DEBUG_MSG("Vehicle::sendPositionsToClient", BOOL)

    def onRammedByAlly(self):
        DEBUG_MSG("Vehicle::onRammedByAlly")

    def requestDamagedDevicesFromFor(self, OBJECT_ID, MAILBOX):
        DEBUG_MSG("Vehicle::requestDamagedDevicesFromFor", OBJECT_ID, MAILBOX)

    def sendDamagedDevicesTo(self, MAILBOX):
        DEBUG_MSG("Vehicle::sendDamagedDevicesTo", MAILBOX)

    def setHonorTitle(self, STRING):
        DEBUG_MSG("Vehicle::setHonorTitle", STRING)

    def receiveTaggedDestructibleKill(self, UINT8):
        DEBUG_MSG("Vehicle::receiveTaggedDestructibleKill", UINT8)

    def setOnFireByExplosion(self, ATTACKER_INFO, SHOT_ID):
        DEBUG_MSG("Vehicle::setOnFireByExplosion", ATT)

    def receiveVisibilityInfo(self, ARRAY, ARRAY_2, ARRAY_3):
        # ARRAY is a list of OBJECT_ID
        # ARRAY_2 is a list of FLOAT32
        # ARRAY_3 is a list of FLOAT32
        DEBUG_MSG("Vehicle::receiveVisibilityInfo", ARRAY, ARRAY_2, ARRAY_3)

    def onTrackAssist(self):
        DEBUG_MSG("Vehicle::onTrackAssist")
