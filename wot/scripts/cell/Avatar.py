import BigWorld

class Avatar( BigWorld.Entity ):
    def __init__( self ):
        BigWorld.Entity.__init__( self )

    def autoAim(self, OBJECT_ID):
        # Exposed tag
        pass

    def moveTo(self, VECTOR3):
        # Exposed tag
        pass

    def bindToVehicle(self, OBJECT_ID):
        # Exposed tag
        pass

    def monitorVehicleDamagedDevices(self, OBJECT_ID):
        # Exposed tag
        pass

    def receiveHorn(self, OBJECT_ID, UINT8, BOOL):
        pass

    def onScoutEvent(self, UINT8, ARRAY):
        # ARRAY is a list of OBJECT_ID
        pass

    def onOwnVehicleStatusChanged(self, INT8, INT8_2, BOOL, BOOL_2):
        pass

    def allowUnbindingFromVehicle(self):
        pass

    def forbidUnbindingFromVehicle(self, INT8):
        pass

    def fullyDiscloseVehicles(self, ARRAY):
        # ARRAY is a list of OBJECT_ID
        pass

    def freezeVisibilityState(self):
        pass

    def receiveVisibilityInfo(self, ARRAY, ARRAY_2, ARRAY_3):
        # ARRAY is a list of OBJECT_ID
        # ARRAY_2 is a list of FLOAT32
        # ARRAY_3 is a list of FLOAT32
        pass

    def receivePositionsFromArena(self, BOOL, ARRAY, ARRAY_2):
        # ARRAY is a list of OBJECT_ID
        # ARRAY_2 is a list of FLOAT32
        pass

    def receiveVehiclePositionFromArena(self, OBJECT_ID, VECTOR3, UINT8):
        pass

    def receiveVehicleDamagedDevices(self, OBJECT_ID, ARRAY, ARRAY_2):
        # ARRAY is a list of EXTRA_ID
        # ARRAY_2 is a list of EXTRA_ID
        pass

    def lockGunOnClient(self, BOOL):
        pass

    def showShotResults(self, ARRAY):
        # ARRAY is a list of UINT64
        pass

    def showTracer(self, OBJECT_ID, UINT8, SHOT_ID, BOOL, BOOL_2, UINT8_2, VECTOR3, VECTOR3_2, VECTOR3_3, FLOAT32, FLOAT32_2):
        pass

    def stopTracer(self, SHOT_ID, VECTOR3):
        pass

    def explodeProjectile(self, SHOT_ID, UINT8, UINT8_2, VECTOR3, VECTOR3_2, ARRAY):
        # ARRAY is a list of UINT32
        pass
