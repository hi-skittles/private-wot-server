"""
A utility library containing data types and functions specifically for 
graph data request functionality.

Contains mostly container classes and AMF conversion functions.
"""

# Import local libraries
import utils

# Import stat_logger modules
import bwsetup
bwsetup.addPath("../../stat_logger")
import prefclasses

# Import Python modules.
import traceback
import logging 
amfLog = logging.getLogger( "stat_grapher.amf" )

# -------------------------------------------------------------------------
# Section: Container classes for serialisation
# -------------------------------------------------------------------------
class ProcessInfo:
	"""Container class for storing information about a process"""
	def __init__( self, dbId, pType, pName, pPid, mName ):
		self.dbId = dbId
		self.pType = pType
		self.name = pName
		self.pid = pPid
		self.machine = mName

	def __str__( self ):
		return "Process %s(%d) on %s" % (self.name, self.pid, self.machine)

class MachineInfo:
	"""Container class for storing information about a machine"""
	def __init__( self, ip, hostname ):
		self.ip = ip
		self.hostname = hostname

	def ipString( self ):
		return utils.inet_ntoa( self.ip )

	def __str__( self ):
		return "Machine %s (%s)" % \
			(self.hostname, self.ipString())

	def __repr__( self ):
		return str( self )

# -------------------------------------------------------------------------
# Section: AMF Conversion functions
# -------------------------------------------------------------------------

def convertToPythonCoreDataType( data ):
	"""
	Converts data, which may be a (complex) user-defined class/type to Python 
	core data type so that it can be converted to AMF data type when response 
	AMF packet is being encoded.

	@param data: Data to be converted.
	"""

	if isinstance( data, list ):
		# It is possible that zero or more elements in the list is 
		# a complex type that need to be converted to Python core data type.
		return [convertToPythonCoreDataType( x ) for x in data]

	elif isinstance( data, MachineInfo ):
		return convertMachineInfoToAMF( data )
			
	elif isinstance( data, ProcessInfo ):
		return convertProcessInfoToAMF( data )

	elif isinstance( data, prefclasses.PrefTree ):
		return convertPrefTreeToAMF( data )

	elif isinstance( data, prefclasses.StatPref ):
		return convertStatPrefToAMF( data )

	elif isinstance( data, prefclasses.WindowPref ):
		return convertWindowPrefToAMF( data )

	else:
		# data already a Python core data type. 
		return data


def convertMachineInfoToAMF( machineInfo ):
	"""
	Converts object of MachineInfo type to Python core data type.

	@param machineInfo: An object of graphutils.MachineInfo type.
	"""

	return dict (
		ip = machineInfo.ipString(),
		hostname = machineInfo.hostname
	)


def convertProcessInfoToAMF( processInfo ):
	"""
	Converts object of ProcessInfo type to Python core data type.

	@param processInfo: An object of graphutils.ProcessInfo type.
	"""
	
	return dict (
		dbId = processInfo.dbId,
		type =  processInfo.pType,
		name = processInfo.name,
		pid = processInfo.pid,
		machine = processInfo.machine,
	)


def convertPrefTreeToAMF( prefTree ):
	"""
	Converts object of prefclasses.PrefTree type to Python core data type.

	@param prefTree: An object of type prefclasses.PrefTree.
	"""

	try:
		ptDict = {}
		ptDict["machineStatPrefs"] = {}
		for msPref in prefTree.iterMachineStatPrefs():
			ptDict[ "machineStatPrefs" ][ str(msPref.dbId) ] = \
				convertStatPrefToAMF( msPref )

		ptDict["procPrefs"] = {}
		for procPref in prefTree.iterProcPrefs():
			ptProcPref = {}
			ptProcPref["name"] = procPref.name
			ptProcPref["dbId"] = procPref.dbId
			ptProcPref["statPrefs"] = {}
			for i in procPref.iterAllStatPrefs():
				ptProcPref["statPrefs"][ str(i.dbId) ] = \
					convertStatPrefToAMF( i )
			ptDict["procPrefs"][procPref.name] = ptProcPref

		ptDict["windowPrefs"] = \
			convertWindowPrefListToAMF( prefTree.windowPrefs )
		ptDict["tickInterval"] = prefTree.tickInterval


		return ptDict

	except Exception, e:
		amfLog.error( traceback.format_exc() )
		amfLog.error( "to_amf_preftree: %s: %s", e.__class__.__name__, e )
		raise e


def convertStatPrefToAMF( statPref ):
	"""
	Converts object of prefclasses.StatPref type to Python core data type.

	@param statPref: An object of prefclasses.StatPref type.
	"""
	try:
		spDict = {}
		spDict["name"] = statPref.name
		spDict["dbId"] = statPref.dbId
		spDict["valueAt"] = statPref.valueAt
		spDict["maxAt"] = statPref.maxAt
		spDict["type"] = statPref.type

		return spDict

	except Exception, e:
		amfLog.error( traceback.format_exc() )
		amfLog.error( "to_amf_statPref: %s: %s", e.__class__.__name__, e )
		raise e


def convertWindowPrefListToAMF( windowPrefList ):
	"""
	Converts each prefclasses.WindowPref object in the list to Python
	core data type.  

	Returns the converted elements in a list.

	@param windowPref: An object of prefclasses.WindowPref type.
	"""

	newWindowPrefList = []
	for i in windowPrefList:
		newWindowPrefList += [convertWindowPrefToAMF( i )]

	return newWindowPrefList


def convertWindowPrefToAMF( windowPref ):
	"""
	Converts object of prefclasses.WindowtPref type to Python core data type.

	@param windowPref: An object of prefclasses.WindowPref type.
	"""

	wpDict = {}
	wpDict["samples"] = windowPref.samples
	wpDict["samplePeriodTicks"] = windowPref.samplePeriodTicks

	return wpDict


