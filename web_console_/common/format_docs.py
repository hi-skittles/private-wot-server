#!/usr/bin/env python

"""
This script generates a table of contents for an HTML file.  At the moment it
assumes top-level headings are <h2>'s (<h1> is the page heading) and generates
entries for <h2>, <h3>, and <h4>.  The source document must contain one element
that looks exactly like this: <div id='__toc__'/>.  This element will be
replaced with the table of contents in the output.

If you want to insert your own heading anchors (so you can #link inside the
document) they must be specified inside the <h*> tag otherwise another anchor
will be created.
"""

import sys
import os
import re
import copy
import logging
import optparse
import htmlentitydefs
from xml.dom import minidom
from xml.sax import saxutils
from HTMLParser import HTMLParser
from cStringIO import StringIO

import bwsetup; bwsetup.addPath( "../.." )

if __name__ == "__main__":
	import pycommon.util
	pycommon.util.setUpBasicCleanLogging()

log = logging.getLogger( __name__ )


class HeaderParser( HTMLParser ):

	def __init__( self, doc, out ):
		HTMLParser.__init__( self )

		anchor = doc.createElement( "div" )
		header = doc.createElement( "h2" )
		header.appendChild( doc.createTextNode( "Contents" ) )

		self.olstack = [doc.createElement( "ul" )]
		self.numstack = [0]

		doc.appendChild( anchor )
		anchor.appendChild( header )
		anchor.appendChild( self.olstack[-1] )

		self.doc = doc
		self.hdrdata = None
		self.hdrname = None
		self.currli = None
		self.headings = []
		self.out = out


	def fmt_attrs( self, attrs ):
		s = " ".join( map( lambda (k,v): '%s="%s"' % (k,v), attrs ) )
		if s.strip():
			return " " + s
		else:
			return ""


	def curr_name( self ):
		return ".".join( map( str, self.numstack ) )


	def dump( self, fmt, *args ):
		if args:
			self.out.write( fmt % args )
		else:
			self.out.write( fmt )


	def handle_starttag( self, tag, attrs ):

		m = re.search( "h([234])", tag )
		if m:
			lvl = int( m.group( 1 ) ) - 1
			self.currli = self.doc.createElement( "li" )
			self.hdrdata = StringIO()

			if len( self.olstack ) > lvl:
				while len( self.olstack ) > lvl:
					self.olstack.pop()
					self.numstack.pop()

			elif len( self.olstack ) == lvl - 1:
				newol = self.doc.createElement( "ul" )
				self.olstack[-1].appendChild( newol )
				self.olstack.append( newol )
				self.numstack.append( 0 )

			self.olstack[-1].appendChild( self.currli )
			self.numstack[-1] += 1

		# Check for headers that have already been named
		if self.hdrdata and tag == "a":
			for k, v in attrs:
				if k == "name":
					self.hdrname = v
					break

		self.dump( "<%s%s>", tag, self.fmt_attrs( attrs ) )


	def handle_endtag( self, tag ):
		m = re.search( "h([234])", tag )

		if m:
			data = ".".join( map( str, self.numstack ) ) + ". " + \
				   self.hdrdata.getvalue()

			if self.hdrname:
				self.dump( data )
			else:
				self.dump( "<a name='%s'/>%s", self.curr_name(), data )

			text = self.doc.createTextNode( saxutils.unescape( data ) )

			anchor = self.doc.createElement( "a" )

			if self.hdrname:
				anchor.setAttribute( "href", "#%s" % self.hdrname )
			else:
				anchor.setAttribute( "href", "#%s" % self.curr_name() )

			anchor.appendChild( text )
			self.currli.appendChild( anchor )

			self.hdrdata = None
			self.hdrname = None
			self.currli = None

		self.dump( "</%s>", tag )

	def handle_data( self, data ):
		if self.hdrdata:
			self.hdrdata.write( data )
		else:
			self.dump( data )


	# The following methods just echo input in the correct format
	def handle_entityref( self, name ):
		if self.hdrdata:
			self.hdrdata.write( "&%s;" % name )
		else:
			self.dump( "&%s;", name )

	def handle_charref( self, name ):
		self.dump( "&#%s;", name )

	def handle_comment( self, text ):
		self.dump( "<!--%s-->", text )

	def handle_decl( self, decl ):
		self.dump( "<!%s>", decl )


def main():

	opt = optparse.OptionParser( globals()[ "__doc__" ] )
	opt.add_option( "--in-place", action = "store_true",
					help = "Modify document in-place" )
	options, args = opt.parse_args()

	if options.in_place:
		outstream = StringIO()
	else:
		outstream = sys.stdout

	process( args[0], outstream )

	if options.in_place:
		outstream.seek( 0 )
		open( args[0], "w" ).write( outstream )

	return 0


def process( filename, outstream ):

	# Parse headings out of input document
	stream = StringIO()
	tocdoc = minidom.Document()
	parser = HeaderParser( tocdoc, stream )
	parser.feed( open( filename ).read() )

	# Re-read document out of modified stream, and find toc anchor point
	stream.seek( 0 )
	doc = minidom.parse( stream )
	anchor = None
	for elt in doc.getElementsByTagName( "div" ):
		if elt.getAttribute( "id" ) == "__toc__":
			anchor = elt

	if not anchor:
		log.critical( "No <div id='__toc__'/> found in input document" )

	# Insert table of contents
	anchor.parentNode.replaceChild( tocdoc.documentElement, anchor )

	# Stream out file with contents
	outstream.write( doc.toxml() )


if __name__ == "__main__":
	sys.exit( main() )
