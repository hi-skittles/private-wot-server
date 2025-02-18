import BigWorld

from bwdebug import DEBUG_MSG


class Avatar(BigWorld.Proxy):
	def __init__(self):
		BigWorld.Proxy.__init__(self)
		self.cellData["position"] = (0, 0, 0)
		self.createCellEntity(BigWorld.globalBases["00_tank_tutorial"].cell)
	
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
		DEBUG_MSG("Avatar::setClientReady")
	
	def leaveArena(self, CLIENT_STATISTICS):
		# Exposed tag
		DEBUG_MSG("Avatar::leaveArena", CLIENT_STATISTICS)
	
	def confirmBattleResultsReceiving(self):
		# Exposed tag
		DEBUG_MSG("Avatar::confirmBattleResultsReceiving")
	
	def doCmdStr(self, INT16, INT16_2, STRING):
		# Exposed tag
		DEBUG_MSG("Avatar::doCmdStr", INT16, INT16_2, STRING)
	
	def doCmdInt3(self, INT16, INT16_2, INT64, INT32, INT32_2):
		# Exposed tag
		DEBUG_MSG("Avatar::doCmdInt3", INT16, INT16_2, INT64, INT32, INT32_2)
	
	def doCmdInt4(self, INT16, INT16_2, INT64, INT32, INT32_2, INT32_3):
		# Exposed tag
		DEBUG_MSG("Avatar::doCmdInt4", INT16, INT16_2, INT64, INT32, INT32_2, INT32_3)
	
	def doCmdInt2Str(self, INT16, INT16_2, INT64, INT32, STRING):
		# Exposed tag
		DEBUG_MSG("Avatar::doCmdInt2Str", INT16, INT16_2, INT64, INT32, STRING)
	
	def doCmdIntArr(self, INT16, INT16_2, ARRAY):
		# ARRAY is a list of INT32
		# Exposed tag
		DEBUG_MSG("Avatar::doCmdIntArr", INT16, INT16_2, ARRAY)
	
	def doCmdIntArrStrArr(self, INT16, INT16_2, ARRAY, ARRAY_2):
		# ARRAY is a list of INT64
		# ARRAY_2 is a list of STRING
		# Exposed tag
		DEBUG_MSG("Avatar::doCmdIntArrStrArr", INT16, INT16_2, ARRAY, ARRAY_2)
	
	def makeDenunciation(self, DB_ID, INT32, INT8):
		# Exposed tag
		DEBUG_MSG("Avatar::makeDenunciation", DB_ID, INT32, INT8)
	
	def banUnbanUser(self, DB_ID, UINT8, UINT32, STRING, INT8):
		# Exposed tag
		DEBUG_MSG("Avatar::banUnbanUser", DB_ID, UINT8, UINT32, STRING, INT8)
	
	def requestToken(self, UINT16, UINT8):
		# Exposed tag
		DEBUG_MSG("Avatar::requestToken", UINT16, UINT8)
	
	def banForTKill(self):
		DEBUG_MSG("Avatar::banForTKill")
	
	def sendAccountStats(self, UINT32, ARRAY):
		# ARRAY is a list of STRING
		# Exposed tag
		DEBUG_MSG("Avatar::sendAccountStats", UINT32, ARRAY)
	
	def setClientCtx(self, STRING):
		# Exposed tag
		DEBUG_MSG("Avatar::setClientCtx", STRING)
	
	def onScoutEvent(self, UINT8, OBJECT_ID):
		DEBUG_MSG("Avatar::onScoutEvent", UINT8, OBJECT_ID)
	
	def updateArena(self, UINT8, STRING, ARRAY):
		# ARRAY is a list of DISCLOSE_EVENT
		DEBUG_MSG("Avatar::updateArena", UINT8, STRING, ARRAY)
	
	def updatePositions(self, ARRAY, ARRAY_2):
		# ARRAY is a list of OBJECT_ID
		# ARRAY_2 is a list of FLOAT32
		DEBUG_MSG("Avatar::updatePositions", ARRAY, ARRAY_2)
	
	def updateOwnVehiclePosition(self, VECTOR3, VECTOR3_2, FLOAT32, FLOAT32_2):
		DEBUG_MSG("Avatar::updateOwnVehiclePosition", VECTOR3, VECTOR3_2, FLOAT32, FLOAT32_2)
	
	def updateGunMarker(self, VECTOR3, VECTOR3_2, FLOAT32):
		DEBUG_MSG("Avatar::updateGunMarker", VECTOR3, VECTOR3_2, FLOAT32)
	
	def updateVehicleHealth(self, INT16, BOOL):
		DEBUG_MSG("Avatar::updateVehicleHealth", INT16, BOOL)
	
	def updateVehicleGunReloadTime(self, OBJECT_ID, FLOAT32, FLOAT32_2):
		DEBUG_MSG("Avatar::updateVehicleGunReloadTime", OBJECT_ID, FLOAT32, FLOAT32_2)
	
	def updateVehicleAmmo(self, INT32, UINT16, UINT16_2, INT16):
		DEBUG_MSG("Avatar::updateVehicleAmmo", INT32, UINT16, UINT16_2, INT16)
	
	def updateVehicleOptionalDeviceStatus(self, UINT8, BOOL):
		DEBUG_MSG("Avatar::updateVehicleOptionalDeviceStatus", UINT8, BOOL)
	
	def updateVehicleMiscStatus(self, OBJECT_ID, UINT8, INT32, FLOAT32):
		DEBUG_MSG("Avatar::updateVehicleMiscStatus", OBJECT_ID, UINT8, INT32, FLOAT32)
	
	def updateVehicleSetting(self, UINT8, INT32):
		DEBUG_MSG("Avatar::updateVehicleSetting", UINT8, INT32)
	
	def updateTargetingInfo(self, FLOAT32, FLOAT32_2, FLOAT32_3, FLOAT32_4, FLOAT32_5, FLOAT32_6, FLOAT32_7, FLOAT32_8,
	                        FLOAT32_9):
		DEBUG_MSG("Avatar::updateTargetingInfo", FLOAT32, FLOAT32_2, FLOAT32_3, FLOAT32_4, FLOAT32_5, FLOAT32_6, FLOAT32_7,)
	
	def showOwnVehicleHitDirection(self, FLOAT32, BOOL):
		DEBUG_MSG("Avatar::showOwnVehicleHitDirection", FLOAT32, BOOL)
	
	def showVehicleDamageInfo(self, OBJECT_ID, UINT8, EXTRA_ID, OBJECT_ID_2):
		DEBUG_MSG("Avatar::showVehicleDamageInfo", OBJECT_ID, UINT8, EXTRA_ID, OBJECT_ID_2)
	
	def showShotResults(self, ARRAY):
		# ARRAY is a list of UINT64
		DEBUG_MSG("Avatar::showShotResults", ARRAY)
	
	def updateBomberTrajectory(self, UINT16, UINT8, FLOAT64, VECTOR3, VECTOR2, FLOAT64_2, VECTOR3_2, VECTOR2_2, BOOL):
		DEBUG_MSG("Avatar::updateBomberTrajectory", UINT16, UINT8, FLOAT64, VECTOR3, VECTOR2, FLOAT64_2, VECTOR3_2, VECTOR2_2, BOOL)
	
	def showHittingArea(self, UINT16, VECTOR3, VECTOR3_2, FLOAT64):
		DEBUG_MSG("Avatar::showHittingArea", UINT16, VECTOR3, VECTOR3_2, FLOAT64)
	
	def showCarpetBombing(self, UINT16, VECTOR3, VECTOR3_2, FLOAT64):
		DEBUG_MSG("Avatar::showCarpetBombing", UINT16, VECTOR3, VECTOR3_2, FLOAT64)
	
	def showDevelopmentInfo(self, UINT8, STRING):
		DEBUG_MSG("Avatar::showDevelopmentInfo", UINT8, STRING)
	
	def vehicle_moveWith(self, UINT8):
		# Exposed tag
		DEBUG_MSG("Avatar::vehicle_moveWith", UINT8)
	
	def vehicle_shoot(self):
		# Exposed tag
		DEBUG_MSG("Avatar::vehicle_shoot")
	
	def vehicle_setEquipmentApplicationPoint(self, UINT16, VECTOR3, VECTOR2):
		# Exposed tag
		DEBUG_MSG("Avatar::vehicle_setEquipmentApplicationPoint", UINT16, VECTOR3, VECTOR2)
	
	def vehicle_trackPointWithGun(self, VECTOR3):
		# Exposed tag
		DEBUG_MSG("Avatar::vehicle_trackPointWithGun", VECTOR3)
	
	def vehicle_stopTrackingWithGun(self, FLOAT32, FLOAT32_2):
		# Exposed tag
		DEBUG_MSG("Avatar::vehicle_stopTrackingWithGun", FLOAT32, FLOAT32_2)
	
	def vehicle_changeSetting(self, UINT8, INT32):
		# Exposed tag
		DEBUG_MSG("Avatar::vehicle_changeSetting", UINT8, INT32)
	
	def vehicle_teleport(self, VECTOR3, FLOAT32):
		# Exposed tag
		DEBUG_MSG("Avatar::vehicle_teleport", VECTOR3, FLOAT32)
	
	def vehicle_replenishAmmo(self):
		# Exposed tag
		DEBUG_MSG("Avatar::vehicle_replenishAmmo")
	
	def vehicle_useHorn(self, BOOL):
		# Exposed tag
		DEBUG_MSG("Avatar::vehicle_useHorn", BOOL)
	
	def createCellNearHere(self, MAILBOX):
		DEBUG_MSG("Avatar::createCellNearHere", MAILBOX)
	
	def onRemovedFromArena(self, UINT64):
		DEBUG_MSG("Avatar::onRemovedFromArena", UINT64)
	
	def onKickedFromArena(self, UINT64, UINT16):
		DEBUG_MSG("Avatar::onKickedFromArena", UINT64, UINT16)
		self.destroy()
	
	def onRoundStarted(self):
		DEBUG_MSG("Avatar::onRoundStarted")
	
	def onRoundFinished(self, INT8, UINT8):
		DEBUG_MSG("Avatar::onRoundFinished", INT8, UINT8)
	
	def setDevelopmentFeature(self, STRING, INT32):
		# Exposed tag
		DEBUG_MSG("Avatar::setDevelopmentFeature", STRING, INT32)
	
	def addBotToArena(self, STRING, UINT8, STRING_2):
		# Exposed tag
		DEBUG_MSG("Avatar::addBotToArena", STRING, UINT8, STRING_2)
	
	def receiveFakeShot(self, INT32, FLOAT32, VECTOR3, VECTOR3_2, UINT8):
		# Exposed tag
		DEBUG_MSG("Avatar::receiveFakeShot", INT32, FLOAT32, VECTOR3, VECTOR3_2, UINT8)
	
	def logStreamCorruption(self, INT16, INT32, INT32_2, INT32_3, INT32_4):
		# Exposed tag
		DEBUG_MSG("Avatar::logStreamCorruption", INT16, INT32, INT32_2, INT32_3, INT32_4)
