import BigWorld
import GUI
import Keys
import CommonDemo
import Math

def init( scriptConfig, engineConfig, preferences, loadingScreenGUI = None):
	global simple
	
	CommonDemo.init( scriptConfig, engineConfig, preferences, loadingScreenGUI )
	CommonDemo.info( "model animation demo" )
	CommonDemo.addHelpInfo([
		"Demo Help:",
		"This demo demonstates models and animations in BigWorld.",
		"",
		"Controls:",
		"A	: move player left",
		"S	: move player backwards",
		"D	: move player right",
		"W	: move player forwards",
		"TAB	: toggle camera",
		"NUM1 	: toggle model change",
		"NUM2 	: toggle model change using background loading",
		"NUM3	: toggle skeleton",
		"NUM4	: toggle action graph",
		"NUM5 	: toggle close up view",
		"NUM6 	: toggle servo motor test",
		"NUM7	: toggle oscillator motor test",
		"UP Arrow	: move platform towards positive z-axis",
		"DOWN Arrow	: move platform towards negative z-axis",
		"RIGHT Arrow	: move platform towards positive x-axis",
		"LEFT Arrow	: move platform towards negative x-axis"])

def start():	
	CommonDemo.start()

def fini():
	global simple
		
	if simple:
		GUI.delRoot(simple)
		simple = None
		
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
	
servo = False
oscillate = False
	
def handleKeyEvent( event ):
	global servo, oscillate
	
	isDown = event.isKeyDown()
	
	if event.key == Keys.KEY_1 and isDown:
		toggleModel()
		return True
	elif event.key == Keys.KEY_2 and isDown:
		toggleBackgroundModel()
		return True
	elif event.key == Keys.KEY_3 and isDown:
		toggleHardPoints()
		return True
	elif event.key == Keys.KEY_4 and isDown:
		toggleActionQueuer()
		return True
	elif event.key == Keys.KEY_5 and isDown:
		toggleModelTexture()
		return True
	elif event.key == Keys.KEY_6 and isDown:
		servo = not servo
		if servo:
			startServoTest()
		return True
	elif event.key == Keys.KEY_7 and isDown:
		oscillate = not oscillate
		oscillatorTest()
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

# demo functions

def toggleModel():
	global servo, oscillate
	
	if BigWorld.player():
		if servo:
			servo = False
		if oscillate:
			oscillate = False
			oscillatorTest()

		BigWorld.player().toggleModel()
		
		CommonDemo.trace("changed player model")
	
def toggleBackgroundModel():
	global servo, oscillate
	
	if BigWorld.player():
		if servo:
			servo = False
		if oscillate:
			oscillate = False
			oscillatorTest()
			
		BigWorld.player().toggleBackgroundModel()
		
		CommonDemo.trace("changing player model in background")
	
hp = False
	
def toggleHardPoints():
	global hp
	
	hp = not hp
	BigWorld.debugModel( hp )
	CommonDemo.trace("toggle skeleton")
	
aq = False

def toggleActionQueuer():
	global aq
	aq = not aq
	
	if aq:
		BigWorld.debugAQ( BigWorld.player().model )
	else:
		BigWorld.debugAQ( None )
	CommonDemo.trace("toggle action graph")
	
render = False
simple = None
scene = None

def toggleModelTexture():
	global render, simple, scene
	
	if simple == None:
		simple = GUI.Simple('A')
		simple.position = (0.5, 0.5, 1)
		simple.materialFX = "SOLID"
		scene = BigWorld.PySceneRenderer( int(BigWorld.screenWidth() / 4) , int(BigWorld.screenHeight() / 4) )
		scene.fov = 1.047
		camera = BigWorld.CursorCamera()
		camera.source = BigWorld.dcursor().matrix
		camera.target = BigWorld.PlayerMatrix()
		camera.pivotPosition = (0.0, 1.0, 0.0)
		camera.reverseView = True
		camera.pivotMaxDist = 2
		scene.cameras = (camera, )
		scene.render()
		simple.texture = scene.texture
		GUI.addRoot(simple)
	
	render = not render
	
	# setup dynamic texture feed
	if render:
		scene.dynamic = True
		simple.visible = True
	else:
		scene.dynamic = False
		simple.visible = False
		
	CommonDemo.trace("toggle model closeup")

# model motors test

particles = []
maxParticles = 20
maxLifeTime = 10.0

class BoxParticle:
	
	def __init__( self, velocity ):
		self.position = BigWorld.player().position
		self.velocity = velocity
		self.model = BigWorld.Model("helpers/models/unit_cube.model")
		BigWorld.player().addModel(self.model)
		self.matrix = Math.Matrix()
		self.matrix.setIdentity()
		self.matrix.setTranslate( self.position )
		self.servo = BigWorld.Servo( self.matrix )
		self.model.addMotor( self.servo )
		self.timer = 0.0
		self.dead = False

	def update( self, dt ):
	
		self.timer += dt
		
		if self.timer > maxLifeTime:
			self.dead = True
			BigWorld.player().delModel(self.model)
		else:
	
			(x, y, z) = self.position
			(vx, vy, vz) = self.velocity
			
			(nx, ny, nz) = (x + dt * vx , y + dt * vy, z + dt * vz)
			
			if ny < 0:
				ny = 0
				
			self.position = (nx, ny, nz)
			
			vx = vx * 0.99
			vy = vy * 0.99 - dt * 4.9
			vz = vz * 0.99		
			
			self.velocity = (vx, vy, vz)
			
			self.matrix.setTranslate( self.position )
			
import random

def startServoTest():
	global particles
	
	generateParticle()
	updateParticles()
	
	CommonDemo.trace("start servo test")
	
def stopServoTest():
	global particles
	
	for p in particles:
		BigWorld.player().delModel(p.model)
	
	particles = []
	
	CommonDemo.trace("stop servo test")
	
def generateParticle():
	global particles
	
	if servo:
	
		vx = random.uniform(-1, 1)
		vy = random.uniform(0, 1)
		vz = random.uniform(-1, 1)
		
		v = 20.0
		
		particles.append( BoxParticle( (vx * v, vy * v, vz * v) ) )
		
		if len(particles) >= maxParticles:
			p = particles[0]
			particles = particles[1:]
			BigWorld.player().delModel(p.model)
			
		BigWorld.callback(0.2, generateParticle)
	else:
		
		stopServoTest()
	
def updateParticles():
	global particles
	
	dt = 0.05
	
	ps = []
	for p in particles:
		p.update(dt)
		if not p.dead:
			ps.append(p)		
	particles = ps
	
	if servo:
		BigWorld.callback(dt, updateParticles)
	
oscillator = None
		
def oscillatorTest():
	global oscillator
	
	if oscillate:
		oscillator = BigWorld.Oscillator( 0, 4, -1 )
		BigWorld.player().model.addMotor( oscillator )
		if hasattr(BigWorld.player().model, "tracker"):
			BigWorld.player().model.tracker = None
		BigWorld.player().model.motors[0].matcherCoupled = False
		CommonDemo.trace("start oscillation")
	else:
		BigWorld.player().model.delMotor( oscillator )
		if hasattr(BigWorld.player().model, "tracker"):
			BigWorld.player().model.tracker = BigWorld.player().tracker
		BigWorld.player().model.motors[0].matcherCoupled = True
		oscillator = None
		CommonDemo.trace("stop oscillation")

def oscillator2Test():
	CommonDemo.trace("oscillator2 test not implemented")
	
def oribitTest():
	CommonDemo.trace("orbit test not implemented")
		
# TrainingDemo.py
