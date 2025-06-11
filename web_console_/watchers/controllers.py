import turbogears

from turbogears.controllers import expose
from turbogears.controllers import redirect
from turbogears import identity

from web_console.common import module

import collections
import filtered_controller
import tree


class Watchers( module.Module ):
	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )
		self.addPage( "Tree", "tree" )
		self.addPage( "Filtered", "filtered" )
		self.addPage( "Collections", "collections" )
		self.addPage( "Help", "help" )

		self.tree = tree.Tree()
		self.filtered = filtered_controller.FilteredController()
		self.collections = collections.Collections()


	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self ):
		raise redirect( turbogears.url( "tree" ) )

# controllers.py
