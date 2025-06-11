import BigWorld
import GUI
import Keys

class DemoGUI:
	
	def __init__( self ):
		
		self.infoLabel = Label()
		self.infoLabel.setColour( ( 255, 255, 0, 255 ) )
		(lw, lh) = self.infoLabel.getSize()
		self.infoLabel.setPosition( ( -lw / 2, -0.9, 1 ) )
		
		self.window = ScrollWindow( 2, 0.5 )
		self.window.setFont( SYSTEM_MEDIUM_FONT )
		self.window.setPosition( ( -1, -0.5, 1 ) )
		
		self.helpWindow = ScrollWindow( 2, 1.5 )
		self.helpWindow.setFont( SYSTEM_LARGE_FONT )
		self.helpWindow.setPosition( ( -1, 1, 1 ) )
		self.helpWindow.disableDrag()
		self.helpWindow.disableFade()
		self.helpWindow.setColour( (255, 255, 0, 255) )
		self.helpWindow.setVisible( False )
		
	def info( self, msg ):
		self.infoLabel.setLabel( msg )
		
	def trace( self, msg ):
		self.window.addMsg( msg )
		
	def helpInfo( self, helpList ):
		for msg in helpList:
			self.helpWindow.addMsg( msg )
			
	def showHelp( self ):
		self.helpWindow.setVisible( True )
		
	def hideHelp( self ):
		self.helpWindow.setVisible( False )
		
		
	def resize( self ):
		# run through the custom resolutions
		(width, height) = BigWorld.screenSize()
		
		if width < 600:
			self.infoLabel.setFont( TINY_FONT )
			self.window.setFont( SYSTEM_TINY_FONT )
			self.helpWindow.setFont( SYSTEM_SMALL_FONT )
		elif width < 800:
			self.infoLabel.setFont( SMALL_FONT )
			self.window.setFont( SYSTEM_SMALL_FONT )
			self.helpWindow.setFont( SYSTEM_MEDIUM_FONT )
		else:
			self.infoLabel.setFont( MEDIUM_FONT )
			self.window.setFont( SYSTEM_MEDIUM_FONT )
			self.helpWindow.setFont( SYSTEM_LARGE_FONT )
		
	def cleanup( self ):
		self.infoLabel.destroy()
		self.window.destroy()
		self.helpWindow.destroy()

# font definitions
TINY_FONT = "default_smaller.font"
SMALL_FONT = "default_small.font"
MEDIUM_FONT = "default_medium.font"
SYSTEM_TINY_FONT = "system_tiny.font"
SYSTEM_SMALL_FONT = "system_small.font"
SYSTEM_MEDIUM_FONT = "system_medium.font"
SYSTEM_LARGE_FONT = "system_large.font"
VERDANA_SMALL_FONT = "verdana_small.font"
VERDANA_MEDIUM_FONT = "verdana_meduium.font"

# static methods

def setComponentColour( component, colour ):
	component.colour[0]  = colour[0]
	component.colour[1] = colour[1]
	component.colour[2] = colour[2]

# gui base class
class SimpleGUI:
	
	def __init__( self, component ):
		self.component = component
		self.component.script = self
		GUI.addRoot( self.component )
		
		if hasattr( self.component, "font" ):
			self.font = self.component.font
			
		self.colour = (255, 255, 255, 255)

	'''
	def __getitem__( self, key ):
		if key == "position":
			return self.getPosition()
		elif key == "size":
			return self.getSize()
		elif key == "font":
			return self.getFont()
		elif key == "colour":
			return self.getColour()
		elif key == "visible":
			return self.getVisible()
		
	def __setitem__( self, key, item ):
		if key == "position":
			self.setPosition( item )
		elif key == "size":
			self.setSize( item )
		elif key == "font":
			self.setFont( item )
		elif key == "colour":
			self.setColour( item )
		elif key == "visible":
			self.setVisible( item )
	'''
			
	def getPosition( self ):
		(x, y, z) = self.component.position
		position = (x - self.component.width * 0.5, y + self.component.height * 0.5, z)
		return position
	
	def setPosition( self, position ):
		(x, y, z) = position
		self.component.position[0] = x + self.component.width * 0.5
		self.component.position[1] = y - self.component.height * 0.5
		
	def getSize( self ):
		return self.component.size
	
	def setSize( self, size ):
		self.component.size = size
		
	def getFont( self ):
		if hasattr( self.component, "font" ):
			return self.component.font
		return ""

	def setFont( self, font ):
		if hasattr( self.component, "font" ):
			self.component.font = font
		
	def getColour( self ):
		return self.colour
	
	def setColour( self, colour ):
		setComponentColour( self.component, colour )
		self.colour = colour
		
	def getVisible( self ):
		return self.component.visible
		
	def setVisible( self, visible ):
		self.component.visible = visible
		
	def addShader( self, shader ):
		self.component.addShader( shader )
		
	def delShader( self, shader ):
		self.component.delShader( shader )
		
	def save( self, filename ):
		self.component.save( filename )
			
	def destroy( self ):
		GUI.delRoot( self.component )
		self.component = None

# simple text label
class Label( SimpleGUI ):
	
	def __init__( self, text = "" ):
		# create a TextGUIComponent
		label = GUI.Text( text )
		
		SimpleGUI.__init__( self, label )
		
		self.setFont( SMALL_FONT )
	
	'''
	def __getitem__( self, key ):
		if key == "text":
			return self.getText()
		else:
			return SimpleGUI.__getitem__( self, key )
	
	def __setitem__( self, key, item ):
		if key == "text":
			self.setText( item )
		else:
			SimpleGUI.__setitem__( self, key , item )
	'''
			
	def getLabel( self ):
		return self.component.text
		
	def setLabel( self, text ):
		self.component.text = text
		
	def destroy( self ):
		SimpleGUI.destroy( self )
	

# simple button label
class Button( SimpleGUI ):
	
	# button states 
	BUTTON_UP = 0   # mouse not over button
	BUTTON_OVER = 1 # mouse over button
	BUTTON_DOWN = 2 # mouse click over button
	
	def __init__( self, label ):
		SimpleGUI.__init__( self, GUI.Simple("") )
		
		self.label = GUI.Text( label )
		self.component.addChild( self.label )
		
		# setup button focus
		self.component.focus = True
		self.component.crossFocus = True
		self.component.script = self
		
		# button callback
		self.onClick = None
		# button fonts
		self.defaultFont = SMALL_FONT
		self.extraFont = MEDIUM_FONT
		# button colours
		self.defaultColour = (255, 255, 255)
		self.extraColour = (255, 255, 0)
		# initial button state
		self.state = self.BUTTON_UP
		
		# draw the button
		self.redraw()
		
	def getLabel( self, str ):
		return self.label.text
		
	def setLabel( self, str ):
		pos = self.getPosition()
		self.label.text = str
		self.component.size = self.label.size
		self.setPosition( pos )
		self.redraw()
		
	def getFont( self ):
		return self.defaultFont

	def setFont( self, font ):
		self.defaultFont = font
		self.redraw()
		
	def getExtraFont( self ):
		return self.extraFont
		
	def setExtraFont( self, font ):
		self.extraFont = font
		self.redraw()
		
	def getColour( self ):
		return self.colour
	
	def setColour( self, colour ):
		self.colour = colour
		self.redraw()
		
	def getExtraColour( self ):
		return self.extraColour
		
	def setExtraColour( self, colour ):
		self.extraColour = colour
		
	# draw the button
	def redraw( self ):
	
		if self.state == self.BUTTON_DOWN:
			self.label.font = self.extraFont
			setComponentColour(self.label, self.extraColour)
		else:
			self.label.font = self.defaultFont
			setComponentColour(self.label, self.defaultColour)
			
		self.component.size = self.label.size
		
		# update label position
		self.label.position = self.component.position
		
	# triggered when mouse moves over the button
	def handleMouseEnterEvent( self, component ):
		self.state = self.BUTTON_OVER
		self.redraw()
		return True
		
	# triggered when mouse moves out of the button
	def handleMouseLeaveEvent( self, component ):
		self.state = self.BUTTON_UP
		self.redraw()
		return True
		
	# triggerd when a key or mouse click event is sent
	def handleKeyEvent( self, event ):
		if self.state != self.BUTTON_UP:
			if event.key == Keys.KEY_LEFTMOUSE:
				if event.isKeyDown():
					self.state = self.BUTTON_DOWN
					self.redraw()
				else:
					# call callback
					if self.onClick and self.state == self.BUTTON_DOWN:
						self.onClick()
						
					self.state = self.BUTTON_OVER
					self.redraw()
				return True
		return False

	def destroy( self ):
		self.component.delChild(self.label)
		self.label = None
		SimpleGUI.destroy( self )


# todo: make window scrollable with scroll buttons and scroll bar
class ScrollWindow( SimpleGUI ):

	def __init__( self, width, height, backgroundImage = None ):
		
		SimpleGUI.__init__( self, GUI.Window("") )
		
		# set background for window 
		# todo: set the material fx for the window
		if backgroundImage:
			self.component.textureName = backgroundImage
			
		self.component.width = width
		self.component.height = height
			
		# add alpha shader for fade in and fade out effects
		alphaShader = GUI.AlphaShader()
		alphaShader.start = -0.5
		alphaShader.stop = 0.5
		alphaShader.mode = "ALL"
		self.alphaShader = alphaShader
		self.component.addShader( alphaShader )
		
		self.fadeTimer = -1
			
		# textfield list
		self.texts = []
		self.textColour = (255, 255, 255)
		self.textFont = SMALL_FONT
		
		# setup window focus
		self.component.focus = True
		self.component.moveFocus = True
		self.component.crossFocus = True
		self.component.script = self
		
		# draw properties
		self.dragEnabled = False
		self.canMove = False
		self.mouseDown = False
		
	def enableFade( self ):
		self.component.addShader( self.alphaShader )
		
	def disableFade( self ):
		self.component.delShader( self.alphaShader )
		
	def getFont( self ):
		return self.textFont
		
	def setFont( self, font ):
		self.textFont = font
		self.redraw()
		
	def getColour( self ):
		return self.textColour
	
	def setColour( self, colour ):
		self.textColour = colour
		self.redraw()
		
	def getSize( self ):
		return self.component.size
	
	def setSize( self, size ):
		self.component.size = size
		self.redraw()
		
	def enableDrag( self ):
		self.dragEnabled = True
		
	def disableDrag( self ):
		self.dragEnabled = False
		
	# add text to the window
	def addMsg( self, msg ):
		# create textfield
		textField = GUI.Text( msg )
		self.texts.append( textField )
		
		# fade in window
		self.alphaShader.alpha = 1.0
		self.alphaShader.speed = 0.5	
		BigWorld.cancelCallback( self.fadeTimer )
		# automatically  fade out after some time has passed
		self.fadeTimer = BigWorld.callback( 5.0, self._fadeOut )
		
		self.redraw()
		
	def _fadeOut( self ):
		self.alphaShader.alpha = 0.0
		self.alphaShader.speed = 1.0
		
	# clear the window
	def clear( self ):
		for textField in self.texts:
			self.component.delChild( textField )
			
	# draw the window
	def redraw( self ):
		# clear the window
		self.clear()
		
		# get the height of a line of text
		if len( self.texts ) == 0:
			height = self._height()
		else:
			height = self.texts[0].height
			
		# get the maximum number of lines for the window
		maxLines = self.component.height / height
		
		# remove top textfield if list is too big
		if len( self.texts ) > maxLines:
			textField = self.texts[0]
			self.texts = self.texts[1:]
		
		# get top left corner
		left = -self.component.width * 0.5
		top = self.component.height * 0.5
		
		# add textfields to window
		for textField in self.texts:
			# set textfield properites
			textField.colour.red = self.textColour[0]
			textField.colour.green = self.textColour[1]
			textField.colour.blue = self.textColour[2]
			textField.font = self.textFont
			textField.position[0] = left + (textField.width * 0.5)
			textField.position[1] = top - (textField.height * 0.5)
				
			# add to window
			self.component.addChild( textField )

			# increment position of next textfield
			top = top - height
			
	def handleMouseEnterEvent( self, component ):
		self.canMove = True
		return True
		
	def handleMouseLeaveEvent( self, component ):
		self.canMove = False
		self.mouseDown = False
		return True
	
	def handleKeyEvent( self, event ):
		if self.dragEnabled and self.canMove:
			if event.key == Keys.KEY_LEFTMOUSE:
				self.lastX = None
				self.lastY = None
				self.mouseDown = event.isKeyDown()
				return True
		return False
			
	def handleMouseEvent( self, component, event ):
		if self.dragEnabled and self.canMove and self.mouseDown:
			if self.lastX:
				self.component.position[0] = self.component.position[0] + (event.cursorPosition.x - self.lastX)
			if self.lastY:
				self.component.position[1] = self.component.position[1] + (event.cursorPosition.y - self.lastY)
			self.lastX = event.cursorPosition.x
			self.lastY = event.cursorPosition.y
			return True
		return False
		
	# cleanup the window
	def destroy( self ):
		# clear window
		self.clear()
		# release textfields
		self.texts = []
		# release alpha shader
		self.alphaShader = None
		# call parent destroy
		SimpleGUI.destroy( self )
		
	# internal function to get the height of a line of text
	def _height( self ):
		t = GUI.Text("TEST")
		t.font = self.textFont
		h = t.height
		del t
		return h