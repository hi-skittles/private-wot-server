import BigWorld
import GUI
import Math
import Keys
import Camera
import SimpleGUI
		
config = None
camera = None
spaceId = None
gui = None

#BIGWORLD PERSONALITYSCRIPT CALLBACKS (refer to python documentation)

def init( scriptConfig, engineConfig, preferences, loadingScreenGUI = None):
	global config, camera, gui
	
	if loadingScreenGUI:
		loadingScreenGUI.visible = False
	
	# setup camera
	camera = Camera.Camera()
	
	# store script config
	config = scriptConfig
	
	# screen gui
	gui = SimpleGUI.DemoGUI()
	gui.info( "server connection demo" )
	gui.helpInfo([
		"Demo Help:",
		"This demo demonstrates how to setup a minimal client that",
		"can connect to the server. ",
		"",
		"Controls:",
		"A		: move player left",
		"S		: move player backwards",
		"D		: move player right",
		"W		: move player forwards",
		"TAB 	: toggle camera"]
	)
	
	trace( "init personality script" )

def start():	
	# check if start in online mode
	isOnline = config.readBool( "online", False )
	if isOnline:
		online()
	else:
		offline()
		
	trace( "start personality script" )

def fini():
	if gui:
		gui.cleanup()

def handleKeyEvent( event ):

	isDown = event.isKeyDown()
	mods = event.modifiers

	if event.key == Keys.KEY_TAB and isDown and not mods == Keys.MODIFIER_ALT:
		toggleCamera()
		return True
	elif event.key == Keys.KEY_ESCAPE and isDown:
		toggleHelp()
		return True
	
	return GUI.handleKeyEvent( event )
	
def handleMouseEvent( event ):
	if camera.handleMouseEvent( event ):
		return True
	
	return GUI.handleMouseEvent( event )

def onRecreateDevice():
	if gui:
		gui.resize()

def onChangeEnvironments( isInside ):
	pass

def onStreamComplete( id, desc, data ):
	pass
	
def onTimeOfDayLocalChange( gameTime, secondsPerGameHour ):
	pass

# Called by app.cpp App::clientChatMsg()
def addChatMsg( id, msg ):
	pass

# These are the python console macro expansions supported by demo
PYTHON_MACROS = {
	"p":"BigWorld.player()",
	"t":"BigWorld.target()",
	"B":"BigWorld"
}

import re

def expandMacros( line ):

	# Glob together the keys from the macros dictionary into a pattern
	patt = "\$([%s])" % "".join( PYTHON_MACROS.keys() )

	def repl( match ):
		return PYTHON_MACROS[ match.group( 1 ) ]

	return re.sub( patt, repl, line )

# INTERNALS

# connect to online space
def online():
	# search for servers
	BigWorld.serverDiscovery.searching = True
		
	# callback to connect to servers
	BigWorld.callback(1, connectToServer )
	
	trace( "online mode" )
	
# try and connect to server
def connectToServer():
	global config
	
	# helper class
	class LogonParams( object ):
		pass
	
	# get ip string from script_config.xml
	ip = config.readString( "ip", "" )
	if ip == "":				
		# no ip tag so search by servername
		servername = config.readString( "servername", "" )
		
		if servername == "":
			trace( "please specify an ip address or server name in script_config.xml" )
			connectionFailed()
			return 
		
		# find server info if one exists
		for i in BigWorld.serverDiscovery.servers:
			if i.ownerName == servername:
				ip = i.serverString
				
		if ip == "":
			trace( "cannot find server [ %s ] on local lan" % servername )
			connectionFailed()
			return 
		
	# connect to server
	BigWorld.connect( ip, LogonParams(), onConnect )
	
	trace( "connecting to " + ip )

# connection callback method (refer to python documentation)
def onConnect( stage, status, err = "" ):	
	if stage == 0:
		trace( "cannot instantiate connection" )
		connectionFailed()
	elif stage == 1:
		if status == 'LOGGED_ON':
			trace( "logged on" )
		else:
			trace( "connection failed" )
			connectionFailed()
	elif stage == 6:
		trace( "connection from server interrupted" )
		connectionFailed()
	elif stage == 2:
		trace( "connection completed" )
		initDemo() # passed
		
# report connection failure
def connectionFailed():
	trace( "switching to offline mode" )
	offline()

# create offline space
def offline():
	global spaceId
	
	# create offline space
	spaceId = BigWorld.createSpace()
	BigWorld.addSpaceGeometryMapping( spaceId, Math.Matrix(), "spaces/demo" )
	
	# callback
	BigWorld.callback( 1, createOfflinePlayer )
	
	trace( "offline mode" )

# create offline player
def createOfflinePlayer():	
	# create player
	playerId = BigWorld.createEntity( "Avatar", spaceId, 0, (0, 0, 0), (0, 0, 1), {} )
	player = BigWorld.entities.get( playerId )
	BigWorld.player( player )
	
	initDemo()
	
	trace( "player created" )
	
# init the demo
def initDemo():
	# set camera
	camera.setCamera( Camera.CURSOR_CAMERA )
	
# toggle camera modes (NORMAL, REVERSE, FREE)
def toggleCamera():
	numOfCameras = 3
	type = (camera.currentCamera + 1) % numOfCameras
	camera.setCamera( type )
	
	if type == Camera.CURSOR_CAMERA:
		trace("cursor camera selected")
	elif type == Camera.REVERSE_CAMERA:
		trace("reverse camera selected")
	else:
		trace("free camera selected")
	
help = False

def toggleHelp():
	global help
	
	help = not help
	
	if help:
		gui.showHelp()
	else:
		gui.hideHelp()
	
def trace( msg ):
	if gui:
		gui.trace( msg )
	
# TrainingDemo.py
