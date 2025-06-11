import BigWorld
import Keys
import CommonDemo

def init( scriptConfig, engineConfig, preferences, loadingScreenGUI = None):
	CommonDemo.init( scriptConfig, engineConfig, preferences, loadingScreenGUI )
	CommonDemo.info( "engine demo" )
	CommonDemo.addHelpInfo( [
		"Demo Help:"] )

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
		
# TrainingDemo.py
