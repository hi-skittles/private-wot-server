import BigWorld
import GUI
import Keys
import Camera
import SimpleGUI
import Math

config = None
spaceId = None
camera = None
gui = None

def init( scriptConfig, engineConfig, preferences, loadingScreenGUI = None):
	global config, camera, gui
	
	if loadingScreenGUI:
		loadingScreenGUI.visible = False
	
	# setup camera
	camera = Camera.Camera()
	
	# store script config
	config = scriptConfig
	
	gui = SimpleGUI.DemoGUI()
	
	GUI.mcursor().clipped = True
	GUI.mcursor().visible = False
	
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
	global gui
	if gui is not None:
		gui.cleanup()
		gui = None
	BigWorld.savePreferences()
	
def handleKeyEvent( event ):
	isDown = event.isKeyDown()
	mods = event.modifiers

	if event.key == Keys.KEY_TAB and isDown and not mods == Keys.MODIFIER_ALT:
		toggleCamera()
		return True
	elif event.key == Keys.KEY_ESCAPE and isDown:
		toggleHelp()
		return True
	elif event.key == Keys.KEY_MINUS and isDown:
		trace("increase field-of-view")
		camera.decreaseFov()
		return True
	elif event.key == Keys.KEY_EQUALS and isDown:
		trace("decrease field-of-view")
		camera.increaseFov()
		return True
	
	handled = GUI.handleKeyEvent( event )
	if not handled:
		# try the camera
		cam = BigWorld.camera()
		if cam is not None:
			handled = cam.handleKeyEvent( event )
			
	return handled
	

def handleMouseEvent( event ):
	camera.handleMouseEvent( event )
	
	handled = GUI.handleMouseEvent( event )
	if not handled:
		# try the camera
		cam = BigWorld.camera()
		if cam is not None:
			handled = cam.handleMouseEvent( event )
			
	return handled

def onRecreateDevice():
	if gui is not None:
		gui.resize()

def onChangeEnvironments( isInside ):
	pass

def onStreamComplete( id, desc, data ):
	pass
	
def onTimeOfDayLocalChange( gameTime, secondsPerGameHour ):
	pass
	
def info( msg ):
	if gui is not None:
		gui.info( msg )
	
def addHelpInfo( commands ):
	if gui is not None:
		gui.helpInfo( commands )
	
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
	
# define models for quick use

AVATAR_MODEL = {
	'files': ('characters/avatars/ranger/ranger_body.model', 'characters/avatars/ranger/ranger_head.model',),
	'matchCaps': [2],
}

STRIFF_MODEL = {
	'files': ('characters/npc/fd_striff/striff.model',),
	'matchCaps': [],
}

SPIDER_MODEL = {
	'files': ('characters/npc/spider/spider.model',),
	'matchCaps': [],
}

ORC_MODEL = {
	'files': ('characters/npc/fd_orc_guard/orc.model',),
	'matchCaps': [2],
}

CRAB_MODEL = {
	'files': ('characters/npc/crab/crab.model',),
	'matchCaps': [],
}

ALL_MODELS = [ 
	AVATAR_MODEL,
	STRIFF_MODEL,
	SPIDER_MODEL,
	ORC_MODEL,
	CRAB_MODEL
]
	
def trace( *args ):
	if gui is not None:
		msg = ""
		for a in args:
			msg = msg + " " + str(a)
		gui.trace( msg )
	
# CommonDemo.py