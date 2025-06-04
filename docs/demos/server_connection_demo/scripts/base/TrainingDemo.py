import BigWorld

def onBaseAppReady( isBootstrap, didAutoLoadEntitiesFromDB ):
	# Only on the first baseapp
	if isBootstrap:
		# Create a Space entity that will create a space with our geometry.
		BigWorld.createBaseLocally( "Space", spaceDir = "spaces/demo" )
						
def onBaseAppShutDown( state ):
	pass

# TrainingDemo.py
