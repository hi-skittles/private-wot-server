from twisted.web import resource, http
from json_convert import asJSON
import BWTwoWay

def returnJSON( request, data ):
	request.setHeader( 'content-type', "application/json" )
	try:
		return asJSON( data )
	except TypeError:
		return returnJSONError( request,
				"Unable to convert %s to JSON" % str( data ) )

def sendJSON( request, data ):
	request.write( returnJSON( request, data ) )
	request.finish()

def returnJSONError( request, error, errorCode = http.FORBIDDEN ):
	request.setHeader( 'content-type', "application/json" )
	request.setResponseCode( errorCode )
	return asJSON( { "excType" : type( error ).__name__, "args" : error.args } )

def sendJSONError( request, error, errorCode = http.FORBIDDEN ):
	request.write( returnJSONError( request, error, errorCode ) )
	request.finish()


class JSONResource( resource.Resource ):
	def getChild( self, name, request ):
		return NotFoundErrorPage()

	def render( self, request ):
		try:
			renderMethod = self.render_GET
		except:
			renderMethod = NotFoundErrorPage().render_GET

		return renderMethod( request )


class ErrorPage( JSONResource ):
	isLeaf = True
	errorCode = http.FORBIDDEN

	def __init__( self, error ):
		JSONResource.__init__( self )
		self.error = error

	def render_GET( self, request ):
		return returnJSONError( request, self.error, self.errorCode )


class NotFoundErrorPage( ErrorPage ):
	errorCode = http.NOT_FOUND

	def __init__( self):
		ErrorPage.__init__( self, BWTwoWay.BWNotFoundError( "No such URL" ) )


class NoSuchEntityErrorPage( ErrorPage ):
	def __init__( self, entityName ):
		ErrorPage.__init__( self, BWTwoWay.BWNoSuchEntityError(
					"No such entity '%s'" % entityName ) )


# json_util.py
