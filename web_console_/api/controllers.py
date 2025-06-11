
import logging
from turbogears import url, identity, expose, redirect
import sys
import os.path

from web_console.common import module

log = logging.getLogger( __name__ )


class HttpApi( module.Module ):

	# blob of API markdown source as a string
	API_SOURCE = ''

	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )
		self.addPage( "Docs", "docs" )

		try:
			self.API_SOURCE = open( os.path.join( 
				os.path.dirname( os.path.abspath( sys.argv[ 0 ] ) ),
				"api/static/http_api.txt" ) ).read()
		except IOError, ex:
			log.error( "Couldn't open API markdown source: %s", ex )
			raise ex
	# __init__


	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self ):
		raise redirect( url( "docs" ) )
	# index


	@identity.require( identity.not_anonymous() )
	@expose( template="common.templates.help" )
	def docs( self ):
		return {
			'helpTopic': "HTTP API - WebConsole",
			'helpContent': self.API_SOURCE,
			'helpFormat': 'markdown',
		}
	# index


# end class HttpApi

# controllers.py
