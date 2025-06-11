import BigWorld
import Keys
import CommonDemo

def init( scriptConfig, engineConfig, preferences, loadingScreenGUI = None):
	CommonDemo.init( scriptConfig, engineConfig, preferences, loadingScreenGUI )
	CommonDemo.info( "entity demo" )
	CommonDemo.addHelpInfo( [
		"Demo Help:",
		"This demo demonstrates the use of entities in the game.",
		"",
		"Controls:",
		"A	: move player left",
		"S	: move player backwards",
		"D	: move player right",
		"W	: move player forwards",
		"TAB	: toggle camera",
		"NUM1 	: toggle filter",
		"NUM2 	: toggle filter visualisation",
		"UP Arrow	: move platform towards positive z-axis",
		"DOWN Arrow	: move platform towards negative z-axis",
		"RIGHT Arrow	: move platform towards positive x-axis",
		"LEFT Arrow	: move platform towards negative x-axis",
		"PgUp	: move platform towards positive y-axis",
		"PgDn	: move platform towards negative y-axis",
		"",
		"Player Controls: commands that can be called on the player entity", 
		"", 
		"spawn( type, position = None ):",
		"\tThis function spawns a single entity",
		"spawnAll( type, count = 1, radius = 20.0 ):",
		"\tThis function spawns the specified number of entities within the given radius",
		"moveAll( radius = 20.0, velocity = 1.0):",
		"\tThis function moves all entities within the specified radius with the given velocity",
		"killAll():",
		"\tThis function kills all entities",
		"capturePlatform( platform ):",
		"\tThis function allows a player to take control of a platform",
		"releasePlatform():",
		"\tThis function releases a platform captured by the player"] )

def start():	
	CommonDemo.start()

def fini():
	CommonDemo.fini()
	
# These are the python console macro expansions supported by Demo
PYTHON_MACROS =	{
	"p":"BigWorld.player()",
	"t":"BigWorld.target()",
	"B":"BigWorld",
}

import re

def expandMacros( line ):

	# Glob together the keys from the macros dictionary into a pattern
	patt = "\$([%s])" % "".join( PYTHON_MACROS.keys() )

	def repl( match ):
		return PYTHON_MACROS[ match.group( 1 ) ]

	return re.sub( patt, repl, line )
	
def handleKeyEvent( event ):

	if event.key == Keys.KEY_1 and event.isKeyDown():
		toggleFilter()
		return True
	elif event.key == Keys.KEY_2 and event.isKeyDown():
		toggleVisual()
		return True
	
	return CommonDemo.handleKeyEvent( event )

def handleMouseEvent( event ):
	return CommonDemo.handleMouseEvent( event )

def onRecreateDevice():
	CommonDemo.onRecreateDevice()

def onChangeEnvironments( isInside ):
	CommonDemo.onChangeEnvironments( isInside )

def onStreamComplete( id, desc, data ):
	CommonDemo.onStreamComplete( id, desc, data )
	
def onTimeOfDayLocalChange( gameTime, secondsPerGameHour ):
	CommonDemo.onTimeOfDayLocalChange( gameTime, secondsPerGameHour )

# Called by app.cpp App::clientChatMsg()
def addChatMsg( id, msg ):
	pass

# INTERNALS
from Platform import Platform

# toggle filter
def toggleFilter():
	global currFilter
	currFilter = (currFilter + 1) % 3
	
	if currFilter == AVATAR_FILTER:
		CommonDemo.trace( "changing to AvatarFilter" )
	elif currFilter == AVATAR_DROP_FILTER:
		CommonDemo.trace( "changing to AvatarDropFilter" )
	else:
		CommonDemo.trace( "changing to DumbFilter" )
	
	for e in BigWorld.entities.values():
		if e.id != BigWorld.player().id and not isinstance(e, Platform):
			e.filter = getFilter()
			
AVATAR_FILTER = 0
AVATAR_DROP_FILTER = 1
DUMB_FILTER = 2

currFilter = 0 # make sure this matches the initial setup of avatar fitler

# get filter given type
def getFilter():
	global currFilter
	
	if currFilter == AVATAR_FILTER:
		return BigWorld.AvatarFilter()
	elif currFilter == AVATAR_DROP_FILTER:
		return BigWorld.AvatarDropFilter()
	else:
		return BigWorld.DumbFilter()
	
import FilterUtilities
visualise = False
	
def toggleVisual():
	global visualise
	
	visualise = not visualise
	
	if visualise:
		FilterUtilities.enableVisualiseAllAvatarFilters()
		CommonDemo.trace( "enable filter visualisation" )
	else:
		FilterUtilities.disableVisualiseAllAvatarFilters()
		CommonDemo.trace( "disable filter visualisation" )
		
# TrainingDemo.py
