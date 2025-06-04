import BigWorld


def onCellAppReady( isFromDB ):
	BigWorld.addSpaceGeometryMapping( 1, None, "spaces/demo" )
	print "Loading spaces/demo"

def onSpaceData( spaceID, entryID, key, value ):
	pass

def onInit( isReload ):
	pass

def onAllSpaceGeometryLoaded( spaceID, isBootstrap, mapping ):
	print "Finished loading space"

# TrainingDemo.py
