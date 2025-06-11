
import cherrypy
import turbogears
import logging
import sys
import os.path

log = logging.getLogger( __name__ )

class Module( turbogears.controllers.Controller ):

	instances = []

	def __init__( self, parent, name, path, icon, auth = (lambda: True), help = None ):

		self.parent = parent
		self.name = name
		self.path = path
		self.icon = icon
		self.pages = []
		self._auth = auth
		self._help = help

		Module.instances.append( self )

	def auth( self ):

		if callable( self._auth ):
			# log.info( "callable auth %s", self.name )
			return self._auth()

		try:
			groups = turbogears.identity.current.groups
			user = turbogears.identity.current.user.user_name
			if self._auth.canAccess( groups ):
				log.debug( "access to module '%s' granted to user %s", self.name, user )
				return True
			else:
				log.info( "access to module '%s' denied to user %s", self.name, user )
				return False
		except:
			return False
	# auth

	def isCurrent( self ):
		return cherrypy.request.path.startswith( "/" + self.path )

	def attrs( self ):
		if self.isCurrent():
			return {"class": "top-level current"}
		else:
			return {"class": "top-level"}

	def header( self ):
		for page in self.pages:
			if page.isCurrent():
				return "%s :: %s" % (self.name, page.name)
		return self.name

	def addPage( self, name, path, **kw ):
		self.pages.append( Page( self, name, path, kw ) )


	@turbogears.expose( template="common.templates.help" )
	def help( self, topic = None ):

		if not topic:
			topic = self.name

		if not topic:
			raise Exception( "Couldn't discern a help topic" )

		# get help content -- can be returned as a file-like object or string, 
		# which will be presumed to be a file name
		helpSrc = self._help
		if not helpSrc:
			raise Exception( "No help available for topic '%s'" % topic )

		if not os.path.isfile( helpSrc ):
			helpSrc = os.path.join(
				os.path.dirname( os.path.abspath( sys.argv[ 0 ] ) ),
				helpSrc )

		try:
			content = open( helpSrc )
		except IOError, ex:
			log.warning( "Couldn't open help file '%s': %s", helpSrc, str( ex ) )
			raise Exception( "No help available for topic '%s'" % topic )

		return {
			"helpTopic": topic,
			"helpContent": content,
		}
	# help


	@classmethod
	def all( self ):
		return self.instances

	@classmethod
	def current( self ):
		for module in self.instances:
			if module.isCurrent():
				return module
		raise RuntimeError, "No module is current.  Wahh!"

class Page( object ):

	def __init__( self, module, name, path, params ):
		self.module = module
		self.name = name
		self.path = path
		self.params = params

	def isCurrent( self ):
		return cherrypy.request.path.startswith(
			"/%s/%s" % (self.module.path, self.path) )

	def attrs( self ):
		if self.isCurrent():
			return {"class": "current"}
		else:
			return {"class": "not-current"}

	def url( self ):
		return turbogears.url( "/%s/%s" % (self.module.path, self.path),
							   **self.params )

# module.py
