import BigWorld

from bwdebug import DEBUG_MSG


class Avatar(BigWorld.Entity):
	def __init__(self):
		BigWorld.Entity.__init__(self)
	
	def autoAim(self, OBJECT_ID):
		# Exposed tag
		DEBUG_MSG('Avatar::autoAim', OBJECT_ID)
	
	def moveTo(self, VECTOR3):
		# Exposed tag
		DEBUG_MSG('Avatar::moveTo', VECTOR3)
	
	def bindToVehicle(self, *args):
		# Exposed tag
		DEBUG_MSG('Avatar::bindToVehicle', args)
	
	def monitorVehicleDamagedDevices(self, OBJECT_ID):
		# Exposed tag
		DEBUG_MSG('Avatar::monitorVehicleDamagedDevices', OBJECT_ID)
	
	def receiveHorn(self, OBJECT_ID, UINT8, BOOL):
		DEBUG_MSG('Avatar::receiveHorn', OBJECT_ID, UINT8, BOOL)
	
	def onScoutEvent(self, UINT8, ARRAY):
		# ARRAY is a list of OBJECT_ID
		DEBUG_MSG('Avatar::onScoutEvent', UINT8, ARRAY)
	
	def onOwnVehicleStatusChanged(self, INT8, INT8_2, BOOL, BOOL_2):
		DEBUG_MSG('Avatar::onOwnVehicleStatusChanged', INT8, INT8_2, BOOL, BOOL_2)
	
	def allowUnbindingFromVehicle(self):
		DEBUG_MSG('Avatar::allowUnbindingFromVehicle')
	
	def forbidUnbindingFromVehicle(self, INT8):
		DEBUG_MSG('Avatar::forbidUnbindingFromVehicle', INT8)
	
	def fullyDiscloseVehicles(self, ARRAY):
		# ARRAY is a list of OBJECT_ID
		DEBUG_MSG('Avatar::fullyDiscloseVehicles', ARRAY)
	
	def freezeVisibilityState(self):
		DEBUG_MSG('Avatar::freezeVisibilityState')
	
	def receiveVisibilityInfo(self, ARRAY, ARRAY_2, ARRAY_3):
		# ARRAY is a list of OBJECT_ID
		# ARRAY_2 is a list of FLOAT32
		# ARRAY_3 is a list of FLOAT32
		DEBUG_MSG('Avatar::receiveVisibilityInfo', ARRAY, ARRAY_2, ARRAY_3)
	
	def receivePositionsFromArena(self, BOOL, ARRAY, ARRAY_2):
		# ARRAY is a list of OBJECT_ID
		# ARRAY_2 is a list of FLOAT32
		DEBUG_MSG('Avatar::receivePositionsFromArena', BOOL, ARRAY, ARRAY_2)
	
	def receiveVehiclePositionFromArena(self, OBJECT_ID, VECTOR3, UINT8):
		DEBUG_MSG('Avatar::receiveVehiclePositionFromArena', OBJECT_ID, VECTOR3, UINT8)
	
	def receiveVehicleDamagedDevices(self, OBJECT_ID, ARRAY, ARRAY_2):
		# ARRAY is a list of EXTRA_ID
		# ARRAY_2 is a list of EXTRA_ID
		DEBUG_MSG('Avatar::receiveVehicleDamagedDevices', OBJECT_ID, ARRAY, ARRAY_2)
	
	def lockGunOnClient(self, BOOL):
		DEBUG_MSG('Avatar::lockGunOnClient', BOOL)
	
	def showShotResults(self, ARRAY):
		# ARRAY is a list of UINT64
		DEBUG_MSG('Avatar::showShotResults', ARRAY)
	
	def showTracer(self, OBJECT_ID, UINT8, SHOT_ID, BOOL, BOOL_2, UINT8_2, VECTOR3, VECTOR3_2, VECTOR3_3, FLOAT32,
	               FLOAT32_2):
		DEBUG_MSG('Avatar::showTracer', OBJECT_ID, UINT8, SHOT_ID, BOOL, BOOL_2, UINT8_2, VECTOR3, VECTOR3_2, VECTOR3_3,
		          FLOAT32, FLOAT32_2)
	
	def stopTracer(self, SHOT_ID, VECTOR3):
		DEBUG_MSG('Avatar::stopTracer', SHOT_ID, VECTOR3)
	
	def explodeProjectile(self, SHOT_ID, UINT8, UINT8_2, VECTOR3, VECTOR3_2, ARRAY):
		# ARRAY is a list of UINT32
		DEBUG_MSG('Avatar::explodeProjectile', SHOT_ID, UINT8, UINT8_2, VECTOR3, VECTOR3_2, ARRAY)
