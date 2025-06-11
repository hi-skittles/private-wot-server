import BigWorld
import Math
import Keys
import CommonDemo
from functools import partial

def init( scriptConfig, engineConfig, preferences, loadingScreenGUI = None):
	CommonDemo.init( scriptConfig, engineConfig, preferences, loadingScreenGUI )
	CommonDemo.info( "game demo" )
	CommonDemo.addHelpInfo( [
		"Demo Help:",
		"This demo demonstrates game specific functionality.",
		"",
		"Controls:",
		"A	: move player left",
		"S	: move player backwards",
		"D	: move player right",
		"W	: move player forwards",
		"TAB	: toggle camera",
		"NUM1	: toggle follow target",
		"NUM2	: toggle trap visualisation"
		"",
		] )
		
class Trap:
	def __init__(self, position, radius):
		self.position = position
		self.radius = radius
		self.matrix = Math.Matrix()
		self.matrix.setTranslate( self.position )
		self.trapID = BigWorld.addPot( self.matrix, self.radius, self.hit )
		self.model = BigWorld.Model("helpers/models/unit_sphere.model")
		
		scale = Math.Matrix()
		scale.setScale( (self.radius, self.radius, self.radius) )
		
		world = Math.Matrix()
		world.setTranslate( self.position )
		
		world.preMultiply(scale)
		
		self.servo = BigWorld.Servo( world )
		self.model.addMotor( self.servo )
		
	def hit( self, enter, trapID ):
		if enter:
			CommonDemo.trace( "entering trap" )
		else:
			CommonDemo.trace( "leaving trap" )
			
	def show( self ):
		BigWorld.player().addModel( self.model )
		
	def hide( self ):
		BigWorld.player().delModel( self.model )

traps = []
		
def start():	
	global traps
	
	CommonDemo.start()
	
	traps.append( Trap( (0, 0, 0), 10.0 ) )
	traps.append( Trap( (20, 0, 20), 5.0) )
	traps.append( Trap( (-30, 0, -10), 10.0) )

def fini():
	CommonDemo.fini()
	
# These are the python console macro expansions supported by Demo
PYTHON_MACROS =	{
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
	
def handleKeyEvent( event ):
	global debugTrap
	
	if event.key == Keys.KEY_1 and event.isKeyDown():
		BigWorld.player().toggleTarget()
		return True
	if event.key == Keys.KEY_2 and event.isKeyDown():
		toggleTrap()
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

trapVisualise = False

def toggleTrap():
	global trapVisualise
	
	trapVisualise = not trapVisualise
	
	if trapVisualise:
		for trap in traps:
			trap.show()
		CommonDemo.trace("show traps")
	else:
		for trap in traps:
			trap.hide()
		CommonDemo.trace("hide traps")
	
# TrainingDemo.py
