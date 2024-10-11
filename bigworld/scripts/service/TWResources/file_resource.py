
import re
import logging
import string
import os

from twisted.internet import reactor, abstract, interfaces
from twisted.python.filepath import FilePath
from twisted.web.resource import Resource, ForbiddenResource
from twisted.web.static import File, StaticProducer, getTypeAndEncoding
from twisted.web.server import NOT_DONE_YET
from twisted.web import http
from zope.interface import implements

import ResMgr
import BigWorld

MATCH_ANYTHING = ( re.compile( r'.' ), )
BW_SERVER_VERSION = BigWorld.getWatcher( 'version/string' )
log = logging.getLogger( __name__ )

class BackgroundProducer( object ):
	"""
	A L{StaticProducer} that writes the entire file to the request.
	To be created and started from the background thread.
	"""

	implements(interfaces.IPullProducer)
	bufferSize = abstract.FileDescriptor.bufferSize

	def __init__( self, request, fileObject ):
		self.request		= request
		self.fileObject		= fileObject

	def start( self ):
		"""
		Starts the producer. Called from background thread.
		"""
		self.stopRequested	= False
		self.isReadingFile	= False
		reactor.callFromThread( self._fgRegister )


	def _fgRegister( self ):
		if self.request:
			self.request.registerProducer( self, 0 )


	def resumeProducing( self ):
		"""
		Resumes producing. Called from main thread.
		"""
		self.isReadingFile = True
		reactor.callInThread( self._bgResumeProducing )

	def _bgResumeProducing( self ):
		data = self.fileObject.read( self.bufferSize )
		reactor.callFromThread( self._fgWrite, data )
			
	def _fgWrite( self, data ):
		"""
		Handles writing of data to request in the main thread.
		"""

		self.isReadingFile = False

		if self.stopRequested:
			reactor.callInThread( self.fileObject.close )
			return

		if data:
			self.request.write(data)
		else:
			self.request.unregisterProducer()
			self.request.finish()
			self.stopProducing()

		
	def stopProducing( self ):
		"""
		L{IPullProducer.stopProducing} is called when our consumer has died.
		This is called from the main thread while the background thread
		may still be running.
		"""
		self.stopRequested = True

		self.request = None

		if not self.isReadingFile:
			reactor.callInThread( self.fileObject.close )

# end class BackgroundProducer

class FileRenderer( Resource, FilePath ):
	"""
	Subclass of twisted L{FilePath} L{Resource} that serves a file, 
	doing sensitive operations in a background thread.
	Adds custom headers.
	"""

	isLeaf      = True
	defaultType = "text/html"

	def __init__( self, documentRoot, relativePath, *args, **kwargs ):

		self.relativePath = relativePath
		self.absolutePath = self.getAbsPath( documentRoot, relativePath )
		
		FilePath.__init__( self, self.absolutePath, *args, **kwargs )

	# __init__
	
	
	def getAbsPath( self, documentRoot, relativePath ):
		if documentRoot != None:
			return os.path.abspath( os.path.join( documentRoot, relativePath ) )
		else:
			return os.path.abspath( relativePath )
			

	def render( self, request ):
		"""
		Renders file with custom headers.
		"""

		log.info(
			"renderFile: %s %s (args: %r).",
			request.method, request.path, request.args
		)

		# add some useful custom headers
		request.responseHeaders.addRawHeader( 'X-BigWorld-Version',
									BW_SERVER_VERSION )
		request.responseHeaders.addRawHeader( 'X-BigWorld-Path',
									self.relativePath )
	
		# set an etag to improve user-agent cache handling
		request.setETag( ":".join( (BW_SERVER_VERSION, self.relativePath) ) )

		if request.method == 'HEAD':
			return ""

		# if web console side send DELETE request, it will delete the original
		# json file
		if request.method == 'DELETE':
			reactor.callInThread( lambda path: os.remove( path ),
				self.absolutePath )
			request.setResponseCode( http.ACCEPTED )
			return ""

		type, encoding = getTypeAndEncoding( self.basename(),
							File.contentTypes,
							File.contentEncodings,
							FileRenderer.defaultType )

		if type:
			request.setHeader('content-type', type)
		if encoding:
			request.setHeader('content-encoding', encoding)

		reactor.callInThread( self._bgContinueRender, request )
		return NOT_DONE_YET

	def _bgContinueRender( self, request ):
		self.restat(False)

		if self.isdir():
			return reactor.callFromThread( 
			  self._renderError, ForbiddenResource(), request )

		if not self.exists():
			return reactor.callFromThread( 
			  self._renderError, File.childNotFound, request )

		if request.setLastModified( self.getmtime() ) is http.CACHED:
			return reactor.callFromThread( 
			  self._renderError, None, request )

		fileSize = self.getsize()
		
		reactor.callFromThread( self._fgEndHeaders, request, fileSize )
		self._bgServeFile( request )


	def _fgEndHeaders( self, request, fileSize ):
		request.setHeader('content-length', str(fileSize))
		request.setResponseCode( http.OK )

	def _bgServeFile( self, request ):
		"""
		Begin sending the contents of this L{File} to the given request.
		Called from the background thread.
		"""

		try:
			fileForReading = self.open()
		except IOError, e:
			import errno
			if e[0] == errno.EACCES:
				reactor.callFromThread( self._renderError, ForbiddenResource(), request )
				return
			else:
				raise

		producer = BackgroundProducer( request, fileForReading )
		producer.start()

	def _renderError( self, errorResource, request ):
		"""
		Renders error resource page. Called from main thread.
		"""
		if errorResource is not None:
			result = errorResource.render( request )
			request.write( result )
		request.finish()

# end class FileRenderer


class ResFileRenderer( FileRenderer ):
	def __init__( self, documentRoot, relativePath, *args, **kwargs ):
		FileRenderer.__init__( self, documentRoot, relativePath,
								*args, **kwargs )
		
		
	def getAbsPath( self, documentRoot, relativePath ):
		return ResMgr.resolveToAbsolutePath( relativePath )	

# end class ResFileRenderer


class ProfileDumpsFileRenderer( FileRenderer ):
	def __init__( self, documentRoot, relativePath, *args, **kwargs ):
		FileRenderer.__init__( self, documentRoot, relativePath,
								*args, **kwargs )
		
		
	def getAbsPath( self, documentRoot, relativePath ):
		# The relative path of profile dumps is already absolute path
		if not relativePath.startswith("/"):
			return "/" + relativePath
		else:
			return relativePath

# end class ProfileDumpsFileRenderer


class FileResource( Resource ):
	"""
	Subclass of twisted L{Resource} implementation for the service of
	files. Default implementation provides for simple regexp-based
	authorisation.

	See also:
	http://twistedmatrix.com/documents/11.0.0/api/twisted.web.iweb.IRequest.html
	"""
	

	def __init__( self, fileRendererCls = FileRenderer,
					whitelist = MATCH_ANYTHING,  documentRoot = None ):
		self.fileRendererCls = fileRendererCls		
		self.documentRoot = documentRoot
		self.children = {}
	
		# sanity check patterns
		for pattern in whitelist:
			try:
				pattern.match( "dummy" )
			except:
				raise ValueError(
					"whitelist argument should be a sequence of regexp objects," \
					" got %r" % whitelist
				)

		#: Sequence of compiled regexp objects
		self.whitelist = whitelist

	# __init__

	def canAccess( self, path ):
		""" Is the client allowed to access this resource? """
		for pattern in self.whitelist:
			if pattern.search( path ) != None:
				return True

		log.debug( "Access to path '%s' denied by whitelist", path );
		return False


	def getChild( self, path, request ):
		if request.postpath:
			relativePath = path + '/' + '/'.join( request.postpath )
		else:
			relativePath = path

		if self.canAccess( relativePath ):
			return self.fileRendererCls( self.documentRoot, relativePath )
		else:
			return ForbiddenResource()
		
	def render( self, request, *args, **kwargs ):
		"""
		Overridden implementation of L{Resource.render}.
		"""
		raise NotImplementedError(self.render)

# end class FileResource

# file_resource.py
