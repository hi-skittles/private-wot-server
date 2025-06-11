# Import standard python libs
from cStringIO import StringIO
import sys
import time
import traceback
import inspect
import cPickle as pickle
import logging

# Import StatGrapher's own modules.
import graphutils

# Import third party libraries
import turbogears
import cherrypy
import pyamf
from pyamf import remoting

# Function decorator which "tags" a function as being exposed
# through the flash AMF gateway
def expose( func ):
	func._exposeAMF = True
	return func

log = logging.getLogger( "stat_grapher.amf" )

# Decorator to allow the use of functions
# This method dispatches calls to the appropriate class methods
class AMFGateway:
	def __init__(self, serviceName = "FlashService"):
		self.amfServiceName = serviceName

	# The main dispatching function
	@turbogears.expose()
	def amfgateway( self ):
		"""
		Processes an AMF packet from the client side.  Each AMF packet may
		contain one or more requests.  Response AMF packet sent back to the
		client contains the responses to those requests.
		The pyamf.remoting.Envelope class represents an AMF packet.
		The pyamf.remoting.Envelope class derives from dict() Python core
		data type.
		"""

		contentType = cherrypy.request.headerMap['Content-Type']
		if contentType != "application/x-amf":
			return self._amfTextResponse()

		try:
			cherrypy.response.headerMap['Content-Type'] = 'application/x-amf'

			log.debug( "=" * 20 )
			log.debug( "amfgateway: Begin handling request" )


			# Decode AMF packet from incoming stream.
			start = time.time()

			inputStream = pyamf.util.BufferedByteStream( cherrypy.request.body.read() )
			envelope = remoting.decode( inputStream, strict=True )

			fromRemotingTime = time.time()

			log.debug( "amfgateway: Unserialising request took %.3f seconds",
				fromRemotingTime - start )


			# Process the received AMF packet and assemble response AMF packet.
			responseEnvelope = self._processAMF( envelope )

			processTime = time.time()

			log.debug( "amfgateway: "
					"Total method processing time took %.3f seconds",
				processTime - fromRemotingTime )


			# Encode response AMF packet to be sent back to the client side.
			out = self._serializeAMF( responseEnvelope )
			serializeTime = time.time()

			log.debug( "amfgateway: Serialising response took %.3f seconds",
				serializeTime - processTime )

			log.debug( "amfgateway: End handling request. Total time was: "
				"%.3f seconds. Size of response: %d bytes.",
				serializeTime - start, len(out) )


			# String containing responses to be stream back to the
			# client-side.
			return out

		except Exception, e:
			cls, e, tb = sys.exc_info()
			details = traceback.format_exception( cls, e, tb )
			log.error ( "Exception in amfgateway method: %s: %s" % \
				(cls.__name__, e) )
			log.error ( ''.join( details ) )
			return None

	def _amfTextResponse( self ):
		output = StringIO()
		output.write("""\
<HTML>
	<HEAD>
		<TITLE>AMF Gateway</TITLE>
		<STYLE type="text/css">
		table
		{
			border: 1px solid black;
			border-collapse: collapse;
			width: 50%%;
		}
		td
		{
			padding: 5px;
			border: 1px solid black;
			color: red;
		}
		th
		{
			padding: 5px;
			text-align: left;
		}
		td.funcname
		{
			width: 30%%;
		}
		body {font-family: Verdana}
		</STYLE>
	</HEAD>

<BODY>
<H1>Flash Remoting gateway</H1>
This is the Flash Remoting gateway, which should be accessed via Flash Remoting.<P>
This gateway provides the "<EM>%s</EM>" service.
The following functions are provided by this gateway: <P>""" % \
			(self.amfServiceName))

		methods = inspect.getmembers( self, self.isAMFMethod )
		output.write( "<TABLE>\n" )
		output.write( "<TR><TH>Function name</TH><TH>Parameters</TH></TR>\n" )

		for name, method in methods:
			output.write( "<TR>" )
			output.write( "<TD class=funcname>%s</TD>" % (name) )

			argList = self.getMethodArgs( method )
			if argList:
				args = ",".join( argList )
			else:
				args = "(Unknown)"
			output.write( "<TD>%s</TD>" % (args) )
			output.write( "</TR>\n" )
		output.write( "</TABLE> </BODY> </HTML>" )
		return output.getvalue()


	def _processAMF( self, envelope ):
		"""
		Processes an AMF packet, which is represented by
		pyamf.remoting.Envelope.

		@param envelope: AMF packet, of type pyamf.remoting.Envelope.
		"""

		if 'DescribeService' in envelope.headers:
			processor = self._processDescription
		else:
			processor = self._processMethod

		path = cherrypy.request.path
		requests = [(request.target, response, request.body) \
			for (response, request) in envelope.iteritems()]

		body = [processor( path, *elem ) for elem in requests]
		body = [b for b in body if b != None]

		# Assemble response to requests using input envelope.
		# Clear old messages in the envelope, which is also
		# a Python dictionary.
		envelope.clear()
		for (targetURI, status, responseURI, value) in body:
			value = graphutils.convertToPythonCoreDataType( value )

			# Add response to one request.
			envelope[targetURI] = remoting.Response( value, status )

		return envelope


	def _serializeAMF( self, envelope ):
		"""
		Encode AMF packet to string so it can be send back to the
		client side.

		@param envelop: AMF packet, of type pyamf.remoting.Envelope, to be
						encoded.
		"""

		# pyamf.remoting.encode returns StringIO object.
		io = remoting.encode( envelope, strict=True )
		cherrypy.response.headerMap['Content-Length'] = str( io.tell() )
		return io.getvalue()

	@staticmethod
	def isAMFMethod( func ):
		return inspect.ismethod( func ) and hasattr( func, "_exposeAMF" )

	@staticmethod
	def getMethodArgs( method ):
		args = inspect.getargspec( method )[0]
		#log.debug( "getMethodArgs: %s", method.__name__ )
		if len(args) > 0 and args[0] == "self":
			return args[1:]
		else:
			return args

	def _processDescription( self, path, target, response, params ):
		"""
		Process "DescribeService" pre-defined header in an AMF packet.

		@param path: Service URL to AMF Gateway.
		@param target: Target URI in the received AMF packet.
		@param response: Response URI in the received AMF packet.
		@param params: List of other parameters.
		"""

		service = target.split('.')[0]
		if service != self.amfServiceName:
			# Ignore...
			return None

		methods = inspect.getmembers( self, self.isAMFMethod )

		functions= []
		for name, method in methods:
			function = {}
			function["description"] = inspect.getdoc( method )
			function["name"] = name
			function["version"] = "1.0"
			function["returns"]= ""
			functions.append( function )

			arguments = []
			argumentList = self.getMethodArgs( method )
			for arg in argumentList:
				argument = {}
				argument["name"] = arg
				argument["required"] = "true"
				argument["type"] = ""
				arguments.append( argument )
			function["arguments"] = arguments

		res = dict(
				version="1.0",
				address=target,
				functions=functions
				)

		return response, remoting.STATUS_OK, 'null', res


	def _processMethod( self, path, target, response, params ):
		"""
		Process a request to invoke a service/method.

		@param path: Service URL to AMF Gateway.
		@param target: Target URI in the received AMF packet.
		@param response: Response URI in the received AMF packet.
		@param params: List of other parameters.
		"""

		try:
			# Process elements of params so that any object of type "object"
			# are changed to "None".  When an AMF data of type "Undefined" is received,
			# that object is decoded/converted to Python object as object().
			params = [self._convertObjectToNone( param ) for param in params]

			# Split the path
			targetElems = target.split( '.' )
			if targetElems[0] != self.amfServiceName:
				raise Exception( "Service \"%s\" not provided. "\
					"The only available service is \"%s\"" % \
						(targetElems[0], self.amfServiceName) )

			# Get the target function to call
			curObj = self
			for targetElem in targetElems[1:]:
				curObj = getattr( curObj, targetElem )
			func = curObj
			if not hasattr( func, "_exposeAMF" ):
				raise Exception(
					"Function \"%s\" is not available over Flash Remoting", func )

			# Call it!
			log.debug("   Calling remote method: %s", target)
			funcStart = time.time()
			res = func( *params )
			log.debug("   Completed calling remote method: %s (took %.3fs)", target,
				time.time() - funcStart)
			status = remoting.STATUS_OK

		except Exception, err:
			cls, e, tb = sys.exc_info()
			details = traceback.format_exception( cls, e, tb )
			status = remoting.STATUS_ERROR
			res = dict(
				code = 'SERVER.PROCESSING',
				level = 'Error',
				description = '%s: %s' % (cls.__name__, e),
				type = cls.__name__,
				details = ''.join( details ),
			)
			log.error ( "%s: %s" % (cls.__name__, e) )
			log.error ( ''.join( details ) )


		return response, status, 'null', res


	def _convertObjectToNone( self, data):
		"""
		If data is of type "object", convert it to None.  Else return data
		without changes.

		@params data: Data to convert, if required.
		"""

		if type( data ) == object:
			return None

		return data

