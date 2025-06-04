import BigWorld
import GUI
import Math
import Keys
import SimpleGUI

# misc colour definitions
EXTRA_COLOUR = (128, 128, 255, 255)
COLOUR = (255, 128, 128, 255)

# gui components
title = SimpleGUI.Label( "GUI Demo Buttons:" )
info = SimpleGUI.Label( "gui demo" )
fade = SimpleGUI.Button( "Fade Out")
drag = SimpleGUI.Button( "Disable Drag" )
colour = SimpleGUI.Button( "White" )
output = SimpleGUI.ScrollWindow( 1, 0.5 )

# gui properites
fadeOut = True
dragEnabled = True
colourWhite = True
alphaShader = None
colourShader = None

def init( scriptConfig, engineConfig, preferences, loadingScreenGUI = None):
	global alphaShader, colourShader
	
	if loadingScreenGUI:
		loadingScreenGUI.visible = False
	
	# setup title label
	title.setFont( SimpleGUI.MEDIUM_FONT )
	title.setPosition( (-0.9, 0.9, 1) )
	
	# setup info label
	(iw, ih) = info.getSize()
	info.setPosition( ( -iw / 2, -0.9, 1) )
	info.setColour( (255, 255, 0) )
	
	# setup output window
	output.setFont( SimpleGUI.SMALL_FONT )
	output.enableDrag()
	output.setPosition( (0.5, 0.4, 1) )
	output.disableFade()
	
	# set alpha shader for output window
	alphaShader = GUI.AlphaShader()
	alphaShader.mode = "ALL"
	alphaShader.start = -0.5
	alphaShader.stop = 0.5
	alphaShader.speed = 1.0
	alphaShader.alpha = 1.0
	
	# set colour shader for output window
	colourShader = GUI.ColourShader()
	colourShader.start = Math.Vector4( 255, 255, 255, 255 )
	colourShader.middle = Math.Vector4( 128, 128, 128, 255 )
	colourShader.end = colourShader.middle
	colourShader.speed = 1.0
	colourShader.value = 0.5
	
	# add shaders to window
	output.addShader(alphaShader)
	output.addShader(colourShader)
	
	# setup fade button	
	fade.setPosition( (-0.9, 0.8, 1) )
	fade.setColour( COLOUR )
	fade.onClick = fadeClick	
	
	# setup colour button
	colour.setPosition( (-0.9, 0.7, 1) )
	colour.setColour( COLOUR )
	colour.onClick = colourClick	
	
	# setup drag button
	drag.setPosition( (-0.9, 0.6, 1) )
	drag.setColour( COLOUR )
	drag.onClick = dragClick
	
	output.addMsg( "init personality script" )
	
def start():
	
	# create offline space
	spaceID = BigWorld.createSpace()	
	BigWorld.addSpaceGeometryMapping( spaceID, None, "spaces/demo" )
	
	# callback to enable mouseControl after some time
	BigWorld.callback(0.5, enableMouseControl )
	
	#output.addMsg( "start personality script" ) # set mouse cursor

def fini():
	
	# destroy gui components
	output.destroy()
	fade.destroy()
	drag.destroy()
	title.destroy()
	info.destroy()
	colour.destroy()
	alphaShader = None
	colourShader = None
	
def handleKeyEvent( event ):
	# allow gui to handle key event
	return GUI.handleKeyEvent( event )

def handleMouseEvent( event ):
	# allow gui to handle mouse event
	return GUI.handleMouseEvent( event )

def onRecreateDevice():
	pass

def onChangeEnvironments( isInside ):
	pass

def onStreamComplete( id, desc, data ):
	pass

def onTimeOfDayLocalChange( gameTime, secondsPerGameHour ):
	pass
	
def expandMacros( line ):
	return line

# Called by app.cpp App::clientChatMsg()
def addChatMsg( id, msg ):
	pass

# INTERNALS

def enableMouseControl():
	# set mouse cursor
	cursor = GUI.mcursor()
	cursor.shape = "arrow"
	cursor.visible = True
	BigWorld.setCursor( cursor )
	
# fade button callback
def fadeClick():
	global fadeOut, alphaShader
	
	if fadeOut:
		alphaShader.alpha = 0.0
	else:
		alphaShader.alpha = 1.0
	
	fadeOut = not fadeOut
	if fadeOut:
		fade.setLabel( "Fade Out" )
		fade.setColour( COLOUR )
		output.addMsg( "Fading In" )
	else:
		fade.setLabel( "Fade In" )
		fade.setColour( EXTRA_COLOUR )
		output.addMsg( "Fading Out" )
	
# colour button callback
def colourClick():
	global colourWhite, colourShader
	
	if colourWhite:
		colourShader.value = 0.0
	else:
		colourShader.value = 0.5
	
	colourWhite = not colourWhite
	if colourWhite:
		colour.setLabel( "White" )
		colour.setColour( COLOUR )
		output.addMsg( "Turning Grey" )
	else:
		colour.setLabel( "Grey" )
		colour.setColour( EXTRA_COLOUR )
		output.addMsg( "Turning White" )
	
# drag button callback
def dragClick():
	global dragEnabled
	
	dragEnabled = not dragEnabled
	if dragEnabled:
		output.enableDrag()
	else:
		output.disableDrag()
		
	if dragEnabled:
		drag.setLabel( "Disable Drag" )
		drag.setColour( COLOUR )
		output.addMsg( "Enabled window dragging" )
	else:
		drag.setLabel( "Enable Drag" )
		drag.setColour( EXTRA_COLOUR )
		output.addMsg( "Disabled window dragging" )
	
# TrainingDemo.py
