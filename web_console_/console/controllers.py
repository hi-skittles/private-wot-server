import telnetlib
import re

# Import standard modules
from datetime import datetime
from StringIO import StringIO
import os
import fnmatch
import logging

# Import third party modules
from turbogears.controllers import (RootController, expose, error_handler,
                                    flash, redirect, validate)
from turbogears import identity
import turbogears
from sqlobject import AND, OR, SQLObject
import sqlobject
import cherrypy
import simplejson

# Import BigWorld modules
import bwsetup; bwsetup.addPath( "../.." )
from pycommon import cluster, watcher_data_type as WDT
from pycommon.exceptions import AuthorisationException, ServerStateException
from web_console.common import ajax
from web_console.common import module
from web_console.common import util
from web_console.common.model import User
from web_console.common.authorisation import Permission

# Import local modules
# import model
#import runscript
#import runscript_db

log = logging.getLogger( "runscript"  )

class PyConsole( object ):

	def __init__( self, host, port ):
		self.host = host
		self.port = port
	# __init__


	def connect( self ):
		tn = None
		result = None
		try:
			tn = telnetlib.Telnet( str( self.host ), str( self.port ) )

			# Read the connection info from the component
			result = tn.read_until( ">>> " )

			return (tn, result[:-6])
		except:
			return (tn, result)
	# connect

# end class PyConsole


# --------------------------------------------------------------------------
# Section: Python console
# --------------------------------------------------------------------------
class Console( module.Module ):

	def __init__( self, *args, **kw ):
		module.Module.__init__( self, *args, **kw )
		self.addPage( "Python", "consoles" )
		self.addPage( "Help", "help" )

		# Reload scripts from file
		try:
			self.loadScriptsFromDir()
			self.removeDeletedScripts()
			self.loadScriptFail = False
		except Exception, e:
			self.loadScriptFail = True
	# __init__


	# Request Processing
	@identity.require( Permission( 'view', 'modify' ) )
	@ajax.expose
	def process_request(self, line, host, port):
		tn = telnetlib.Telnet( str(host), str(port) )

		# Read the connection info from the component
		tn.read_until( ">>> " )

		# do the line write / read
		result = self.process_line(tn, line)

		# Close the session
		tn.close()

		# Prefix the command with a python console indicator, and
		# strip off the trailing console marks as well as the
		# \r\n that telnet has sent through
		result = ">>> " + result[:-6]

		return dict( more=False, output=result )


	def process_line(self, tn, line):
		line = line + "\r\n"

		# Write out the command
		tn.write( str( line ) )

		# Read back the response (including the command executed)
		(index, regex, result) = tn.expect( [ ">>> ", "\.\.\. " ] )

		return result


	# Multiline processing
	@identity.require( Permission( 'view', 'modify' ) )
	@ajax.expose
	def process_multiline_request(self, block, host, port):
		(tn, output) = self.connect( host, port )

		if tn:
			# Force a final line after the text block to ensure
			# any indented code is executed by the interpreter
			block = block + "\n"

			lines = [line for line in block.split('\n')]

			output = ""
			for line in lines:
				output = output + self.process_line( tn, line )

			# Close the session
			tn.close()

			# Prefix the command with a python console indicator, and
			# strip off the trailing console marks as well as the
			# \r\n that telnet has sent through
			output = ">>> " + output[:-6]

		return dict( more=False, output=output )


	def connect(self, host, port):
		tn = None
		result = None
		try:
			tn = telnetlib.Telnet( str(host), str(port) )

			# Read the connection info from the component
			result = tn.read_until( ">>> " )

			return (tn, result[:-6])
		except:
			return (tn, result)


	## Main console
	@identity.require( Permission( 'view', 'modify' ) )
	@expose( template="console.templates.console" )
	def console( self, host, port = None, process = '', user=None, tg_errors=None ):

		if process and not port:
			userObj = util.getUser( cluster.cache.get(), user )
			procs = [p for p in userObj.getProcs() if p.hasPythonConsole ]
			for p in procs:
				if process == p.label():
					port = p.getWatcherValue( "pythonServerPort" )
					break

			if not port:
				raise Exception(
					"Couldn't discover pythonServerPort for %s on %s" % \
					(process, host) )

		tn, banner = self.connect( host, port )
		if tn:
			tn.close()
		banner = re.sub( "\r\n", " - ", banner)
		return dict( hostname = host, port = port,
					 process_label = process, banner = banner )
	# console


	@identity.require( Permission( 'view', 'modify' ) )
	@expose( template="console.templates.list" )
	def consoles( self ):

		c = cluster.cache.get()
		user = util.getUser( c )

		# Generate list of processes that have a python console
		procs = sorted( [p for p in user.getProcs() if p.hasPythonConsole ] )

		# Generate mapping for python ports
		ports = {}
		procsToRemove = set()
		for p in procs:
			port = p.getWatcherValue( "pythonServerPort" )
			if port:
				ports[ p ] = port
			else:
				#procs.remove( p )
				procsToRemove.add( p )

		for p in procsToRemove:
			procs.remove( p )

		# Generate labels
		labels = {}
		for p in procs:
			labels[ p ] = "%s on %s" % (p.label(), p.machine.name)

		return dict( procs = procs, ports = ports, labels = labels,
					 user = user )


	# --------------------------------------------------------------------------
	# Section: Misc
	# --------------------------------------------------------------------------
	@identity.require( identity.not_anonymous() )
	@expose()
	def index( self ):
		raise redirect( "consoles" )

# end class Console

