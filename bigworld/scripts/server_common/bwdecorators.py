import BigWorld

def callableOnGhost( f ):
	"""
	This is a decorator that should be added to methods that can validly be
	called on ghost entities.

	For example:

	import bwdecorators
	class Table( BigWorld.Entity ):
		@bwdecorators.callableOnGhost
		def getArea( self ):
			return self.width * self.height
	"""

	f.isGhost = True
	return f


def eventListener( event ):
	"""
	This decorator is used to add methods as event listeners.
	"""
	def wrapper( f ):
		BigWorld.addEventListener( event, f )
		return f

	return wrapper


def watcher( path ):
	"""
	This decorator calls BigWorld.addWatcher for the given function. This
	decorator also adds a new decorator instance to the function under the
	"setter" attribute, so that it can be used to decorate the setter function
	for the watcher.

	e.g.

	@watcher( path )
	def myWatcher():
		return someValue()

	@myWatcher.setter
	def myWatcher( value ):
		setSomeValue( value )
	"""
	def decorator( f ):
		def decoratorSetter( g ):
			BigWorld.delWatcher( path )
			BigWorld.addWatcher( path, f, g )
			return g
		f.setter = decoratorSetter
		BigWorld.addWatcher( path, f )
		return f
	return decorator


def functionWatcher( path, exposure, description ):
	"""
	This decorator and the associated functionWatcherParameter decorator can be
	used to describe a function watcher.

	e.g.

	@functionWatcher( "command/myCommand", BigWorld.EXPOSE_BASE_APPS, 
		"This is my command description " )
	@functionWatcherParameter( int, "First parameter" )
	@functionWatcherParameter( str, "Second parameter" )
	def myCommand( first, second ):
		...

	@param path 		The path of the function watcher to add.
	@param exposure 	The exposure of the function watcher.
	@param description 	The human-readable description of the function watcher.
	"""
	def decorator( f ):
		if not hasattr( f, "params" ):
			f.params = []
		BigWorld.addFunctionWatcher( path, f, f.params, exposure, description )
		return f

	return decorator


def functionWatcherParameter( paramType, description ):
	"""
	This decorator specifies a parameter to be added for the associated
	function watcher.

	This decorator and the associated functionWatcher decorator can be used to
	describe a function watcher. 

	@param paramType 	The parameter type.
	@param description 	The human-readable description of the parameter.
	"""
	def decorator( f ):
		if not hasattr( f, "params" ):
			f.params = []
		f.params.insert( 0, (description, paramType) )
		return f

	return decorator


# bwdecorators.py
