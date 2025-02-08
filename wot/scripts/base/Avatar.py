import BigWorld

class Avatar(BigWorld.Proxy):
    def __init__(self):
        BigWorld.Proxy.__init__(self)
        
    def onClientDeath(self):
        # When the client disconnects, we want to make sure our cell entity
        # doesn't hang around.
        self.destroyCellEntity()
    
    def onLoseCell(self):
        # Once our cell entity is destroyed, it's safe to clean up the Proxy.
        # We can't just call self.destroy() in onClientDeath() above, as
        # destroyCellEntity() is asynchronous and the cell entity would still
        # exist at that point.
        self.destroy()

    def setClientReady(self):
        # Exposed tag
        pass

    def leaveArena(self, CLIENT_STATISTICS):
        # Exposed tag
        pass

    def confirmBattleResultsReceiving(self):
        # Exposed tag
        pass

    def doCmdStr(self, INT16, INT16_2, STRING):
        # Exposed tag
        pass

    def doCmdInt3(self, INT16, INT16_2, INT64, INT32, INT32_2):
        # Exposed tag
        pass

    def doCmdInt4(self, INT16, INT16_2, INT64, INT32, INT32_2, INT32_3):
        # Exposed tag
        pass

    def doCmdInt2Str(self, INT16, INT16_2, INT64, INT32, STRING):
        # Exposed tag
        pass

    def doCmdIntArr(self, INT16, INT16_2, ARRAY):
        # ARRAY is a list of INT32
        # Exposed tag
        pass

    def doCmdIntArrStrArr(self, INT16, INT16_2, ARRAY, ARRAY_2):
        # ARRAY is a list of INT64
        # ARRAY_2 is a list of STRING
        # Exposed tag
        pass

    def makeDenunciation(self, DB_ID, INT32, INT8):
        # Exposed tag
        pass

    def banUnbanUser(self, DB_ID, UINT8, UINT32, STRING, INT8):
        # Exposed tag
        pass

    def requestToken(self, UINT16, UINT8):
        # Exposed tag
        pass

    def banForTKill(self):
        pass

    def sendAccountStats(self, UINT32, ARRAY):
        # ARRAY is a list of STRING
        # Exposed tag
        pass

    def setClientCtx(self, STRING):
        # Exposed tag
        pass

    def onScoutEvent(self, UINT8, OBJECT_ID):
        pass

    def updateArena(self, UINT8, STRING, ARRAY):
        # ARRAY is a list of DISCLOSE_EVENT
        pass

    def updatePositions(self, ARRAY, ARRAY_2):
        # ARRAY is a list of OBJECT_ID
        # ARRAY_2 is a list of FLOAT32
        pass

    def updateOwnVehiclePosition(self, VECTOR3, VECTOR3_2, FLOAT32, FLOAT32_2):
        pass

    def updateGunMarker(self, VECTOR3, VECTOR3_2, FLOAT32):
        pass

    def updateVehicleHealth(self, INT16, BOOL):
        pass

    def updateVehicleGunReloadTime(self, OBJECT_ID, FLOAT32, FLOAT32_2):
        pass

    def updateVehicleAmmo(self, INT32, UINT16, UINT16_2, INT16):
        pass

    def updateVehicleOptionalDeviceStatus(self, UINT8, BOOL):
        pass

    def updateVehicleMiscStatus(self, OBJECT_ID, UINT8, INT32, FLOAT32):
        pass

    def updateVehicleSetting(self, UINT8, INT32):
        pass

    def updateTargetingInfo(self, FLOAT32, FLOAT32_2, FLOAT32_3, FLOAT32_4, FLOAT32_5, FLOAT32_6, FLOAT32_7, FLOAT32_8, FLOAT32_9):
        pass

    def showOwnVehicleHitDirection(self, FLOAT32, BOOL):
        pass

    def showVehicleDamageInfo(self, OBJECT_ID, UINT8, EXTRA_ID, OBJECT_ID_2):
        pass

    def showShotResults(self, ARRAY):
        # ARRAY is a list of UINT64
        pass

    def updateBomberTrajectory(self, UINT16, UINT8, FLOAT64, VECTOR3, VECTOR2, FLOAT64_2, VECTOR3_2, VECTOR2_2, BOOL):
        pass

    def showHittingArea(self, UINT16, VECTOR3, VECTOR3_2, FLOAT64):
        pass

    def showCarpetBombing(self, UINT16, VECTOR3, VECTOR3_2, FLOAT64):
        pass

    def showDevelopmentInfo(self, UINT8, STRING):
        pass

    def vehicle_moveWith(self, UINT8):
        # Exposed tag
        pass

    def vehicle_shoot(self):
        # Exposed tag
        pass

    def vehicle_setEquipmentApplicationPoint(self, UINT16, VECTOR3, VECTOR2):
        # Exposed tag
        pass

    def vehicle_trackPointWithGun(self, VECTOR3):
        # Exposed tag
        pass

    def vehicle_stopTrackingWithGun(self, FLOAT32, FLOAT32_2):
        # Exposed tag
        pass

    def vehicle_changeSetting(self, UINT8, INT32):
        # Exposed tag
        pass

    def vehicle_teleport(self, VECTOR3, FLOAT32):
        # Exposed tag
        pass

    def vehicle_replenishAmmo(self):
        # Exposed tag
        pass

    def vehicle_useHorn(self, BOOL):
        # Exposed tag
        pass

    def createCellNearHere(self, MAILBOX):
        pass

    def onRemovedFromArena(self, UINT64):
        pass

    def onKickedFromArena(self, UINT64, UINT16):
        pass

    def onRoundStarted(self):
        pass

    def onRoundFinished(self, INT8, UINT8):
        pass

    def setDevelopmentFeature(self, STRING, INT32):
        # Exposed tag
        pass

    def addBotToArena(self, STRING, UINT8, STRING_2):
        # Exposed tag
        pass

    def receiveFakeShot(self, INT32, FLOAT32, VECTOR3, VECTOR3_2, UINT8):
        # Exposed tag
        pass

    def logStreamCorruption(self, INT16, INT32, INT32_2, INT32_3, INT32_4):
        # Exposed tag
        pass
