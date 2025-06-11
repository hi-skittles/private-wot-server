"""
DisplayPref classes and functionality for use with StatGrapher clients.
"""
# Import standard modules
import logging
import os
import copy

# Import local modules
import managedb
import model
import utils

# Import third party modules
import turbogears

# Import StatLogger modules
import prefxml

# Logging modules
apiLog = logging.getLogger( "stat_grapher.api" )

# -------------------------------------------------------------------------
# Section: PrefRequester
# -------------------------------------------------------------------------
class PrefRequester:
	def __init__( self, backend ):
		"""
		PrefRequester constructor. Takes in a StatGrapher backend
		(not used, but just in case)
		"""
		self.backend = backend
		self.defaultDisplayPrefs = {}    # {logDb -> displayPrefDict}
		self.userDisplayPrefs = {}       # {logDb,user -> displayPrefDict}
		self.options = None              # Options loaded from XML file
		self.xmlPrefTree = None          # PrefTree loaded from XML file
		self.prefFileModified = None     # Timestamp of XML file modification
		self.prefFileName = os.path.abspath( 
				turbogears.config.get( "stat_logger.preferences",
										"../stat_logger/preferences.xml" )
				)

	# -------------------------------------------------------------------------
	# Section: PrefRequester Public functions
	# -------------------------------------------------------------------------
	def retrieveOptions( self ):
		"""
		Request the global stat_logger options
		"""
		self._checkPrefFileModified()
		return copy.deepcopy( self.options )

	def retrieveDisplayPrefs( self, logDb, sessionUser ):
		"""
		Request the display preferences for this user and log. Main function
		to get display preferences.
		"""
		# Retrieve or generate default display preferences as a basis
		defaultPrefs = self._retrieveDefaultDisplayPrefs( logDb )
		outDict = copy.deepcopy( defaultPrefs )

		# Get the user's display prefs
		userPrefs = self.retrieveUserDisplayPrefs( logDb, sessionUser )
		userDict = userPrefs.dict()

		# Now merge default and user preferences into a single dictionary
		for procName, procPref in userDict["procPrefs"].iteritems():
			for statId, valueDict in procPref.iteritems():
				outDict["procPrefs"][procName][str( statId )].update(
					valueDict )

		for procType, enabledStats in \
				userDict[ "enabledProcStatOrder" ].iteritems():
			outDict["enabledProcStatOrder"][procType] = enabledStats

		for statId, valueDict in userDict[ "machineStatPrefs" ].iteritems():
			outDict["machineStatPrefs"][str( statId )].update( valueDict )

		if userDict[ "enabledMachineStatOrder" ]:
			outDict["enabledMachineStatOrder"] = \
				userDict[ "enabledMachineStatOrder" ]

		#apiLog.debug( "requestDisplayPrefs: returning %r", outDict )
		return outDict

	def retrieveUserDisplayPrefs( self, logDb, user ):
		"""
		Get the pure user display preferences for a given user and log
		database. Needs to be "merged" with the default prefs.
		"""
		try:
			return self.userDisplayPrefs[ logDb, user ]
		except KeyError:
			newPref = UserDisplayPref( logDb, user )
			self.userDisplayPrefs[ (logDb, user) ] = newPref
			return newPref

	def setProcessStatColour( self, logDb, user, procType, prefId, newColour ):
		"""
		Saves a colour change to the database.

		@param logDb		the log database
		@param user			the session user object
		@param procType		the process type
		@param prefId		the dbId of the process statPref
		@param newColour	the new colour (6 digit rgb hex string)
		"""
		userPrefs = self.retrieveUserDisplayPrefs( logDb, user )
		procPrefsDict = userPrefs.dict().setdefault( "procPrefs", {} )
		procTypeDict = procPrefsDict.setdefault( procType, {} )
		prefIdDict = procTypeDict.setdefault( prefId, {} )
		if newColour == None:
			try:
				del prefIdDict[ "colour" ]
			except: pass
		else:
			prefIdDict[ "colour" ] = newColour
		userPrefs.updateToDB()
		apiLog.debug( "setProcessStatColour: colour has been set" )

	def setMachineStatColour( self, logDb, user, prefId, newColour ):
		"""
		Saves a colour change to the database.

		@param logDb		the log database
		@param user			the user id
		@param prefId		the dbId of the machine statPref
		@param newColour	the new colour (6 digit rgb hex string)
		"""
		userPrefs = self.retrieveUserDisplayPrefs( logDb, user )
		machinePrefsDict = userPrefs.dict().setdefault( "machineStatPrefs", {} )
		prefIdDict = machinePrefsDict.setdefault( prefId, {} )
		if newColour == None:
			try:
				del prefIdDict[ "colour" ]
			except: pass
		else:
			prefIdDict[ "colour" ] = newColour
		userPrefs.updateToDB()
		apiLog.debug( "setMachineStatColour: colour has been set" )

	def saveEnabledProcStatOrder( self, logDb, user, procType, statList ):
		"""
		Save the process statistics order list for the given log and process
		type.

		@param logDb		the log database
		@param procType		the process type
		@param statList 	list of ordered stat ids in unicode string form
		"""
		utils.logArgs( apiLog.debug )
		userPrefs = self.retrieveUserDisplayPrefs( logDb, user )
		userDict = userPrefs.dict()
		enabledProcStatOrder = userDict.setdefault( "enabledProcStatOrder", {} )
		enabledProcStatOrder[procType] = statList
		userPrefs.updateToDB()

	def saveEnabledMachineStatOrder( self, logDb, user, statList ):
		"""
		Save the machine statistics order list for the given log.

		@param logDb		the log database
		@param statList		list of ordered statistic IDs in unicode string form
		"""
		utils.logArgs( apiLog.debug )
		userPrefs = self.retrieveUserDisplayPrefs( logDb, user )
		userDict = userPrefs.dict()
		userDict["enabledMachineStatOrder"] = statList
		userPrefs.updateToDB()

	# -------------------------------------------------------------------------
	# Section: PrefRequester Internal functions
	# -------------------------------------------------------------------------
	def _checkPrefFileModified( self ):
		"""
		Checks if the preferences xml file has been modified, and
		if so, clears and reloads our options and xmlPrefTree
		Returns True if the file was reloaded
		"""
		# Check if the "preferences.xml" file has been
		# modified, otherwise reload everything
		newPrefFileModified = os.stat( self.prefFileName )
		if newPrefFileModified != self.prefFileModified:
			self.options, self.xmlPrefTree = prefxml.loadPrefsFromXMLFile(
				self.prefFileName )
			self.prefFileModified = newPrefFileModified

			# Clear our cached default preferences
			self.defaultDisplayPrefs.clear()
			return True
		return False

	def _retrieveDefaultDisplayPrefs( self, logDb ):
		"""
		Generates the default display prefs for a given logDb
		"""
		self._checkPrefFileModified()
		# Try and return default preferences from our cache
		try:
			return self.defaultDisplayPrefs[logDb]
		except KeyError: pass

		xmlPrefTree = self.xmlPrefTree
		dbManager, dbPrefTree = managedb.ptManager.requestDbManager( logDb )

		# build display prefs dictionary
		displayPrefs = {
			# {Process Type->Ordered list of StatPref IDs}
			"enabledProcStatOrder"		: {},
			# {Process Type->{StatPref ID->{"colour"->col}}}
			"procPrefs"					: {},
			# {Process Type->Ordered list of StatPref IDs}
			"enabledMachineStatOrder"	: [],
			# {StatPref ID->{"colour"->col}}
			"machineStatPrefs"			: {}
		}

		enabledProcStatOrder = displayPrefs['enabledProcStatOrder']
		enabledMachineStatOrder = displayPrefs['enabledMachineStatOrder']

		for dbProcPref in dbPrefTree.iterProcPrefs():
			xmlProcPref = xmlPrefTree.procPrefByName( dbProcPref.name )
			enabledProcStatOrder[dbProcPref.name] = []
			displayPrefs[ "procPrefs" ][ dbProcPref.name ] = {}
			for dbProcStatPref in dbProcPref.iterAllStatPrefs():
				statPrefId = str( dbProcStatPref.dbId )

				displayStatPref = {}
				displayPrefs["procPrefs"][dbProcPref.name][statPrefId] = \
					displayStatPref

				# Retrieve "colour" and "show" attribute from statPref
				try:
					xmlProcStatPref = xmlProcPref.statPrefByName(
						dbProcStatPref.name )
					statColour = xmlProcStatPref.colour
					statShow = xmlProcStatPref.show
					statDescription = xmlProcStatPref.description
				except KeyError:
					statColour = prefxml._randomColour()
					statShow = False
					statDescription = "Description not available."

				displayStatPref["colour"] = "%06X" % statColour

				if statShow:
					enabledProcStatOrder[dbProcPref.name].append( statPrefId )

				displayStatPref["description"] = statDescription

		# Combine machine branches
		for dbMachineStatPref in dbPrefTree.iterMachineStatPrefs():

			statPrefId = str( dbMachineStatPref.dbId )

			displayStatPref = {}
			displayPrefs["machineStatPrefs"][statPrefId] = displayStatPref

			try:
				xmlMachineStatPref = xmlPrefTree.machineStatPrefByName(
					dbMachineStatPref.name )
				statColour = xmlMachineStatPref.colour
				statShow = xmlMachineStatPref.show
				statDescription = xmlMachineStatPref.description
			except KeyError:
				statColour = prefxml._randomColour()
				statShow = False
				statDescription = "Description not available."
			displayStatPref["colour"] = "%06X" % statColour

			if statShow:
				enabledMachineStatOrder.append( statPrefId )

			displayStatPref["description"] = statDescription

		self.defaultDisplayPrefs[logDb] = displayPrefs
		#apiLog.info( "UserDisplayPrefs._generateDisplayPrefs: returning %r", displayPrefs )
		return displayPrefs


# -------------------------------------------------------------------------
# Section: UserDisplayPref
# -------------------------------------------------------------------------
class UserDisplayPref:
	"""
	In-memory copy of the user display preferences array (specific to a user
	and a log database) from the StatGrapherPrefs sqlobject-based database
	table. Retrieved on init time from StatLogger's preference file, and
	updates to this object propagate to the database table.
	"""

	def __init__( self, logDb, user ):
		"""
		Constructor. Passing None for the user retrieves the default preferences.

		@param logDb:	the log database
		@param user:		the user ID
		"""
		self.logDb = str( logDb )
		self.user = user
		self.refreshFromDB()


	def dict( self ):
		"""
		Return the dictionary containing the user display preferences.
		Modifications to this dictionary can be updated to the database through
		the updateToDB method.
		"""
		return self._displayPrefs


	def updateToDB( self ):
		"""
		Save the preferences to the database.
		"""
		rows = model.StatGrapherPrefs.selectBy(
			userID = self.user.id,
			log = self.logDb )
		record = rows[0]
		record.displayPrefs = self._displayPrefs


	def refreshFromDB( self ):
		"""
		Refreshes the dictionary taking values from the DB.
		"""
		rows = model.StatGrapherPrefs.selectBy(
			userID = self.user.id,
			log = self.logDb )
		if rows.count() == 1:
			record = rows[0]
		else:
			displayPrefs = {
				"enabledProcStatOrder" 		: {},
				"procPrefs"					: {},
				"enabledMachineStatOrder"	: [],
				"machineStatPrefs"			: {}
			}
			record = model.StatGrapherPrefs(
				user = self.user,
				log = self.logDb,
				displayPrefs = displayPrefs )

		self._displayPrefs = record.displayPrefs
