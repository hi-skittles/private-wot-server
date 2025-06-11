ARGS = (
# CellApp Filters
("Cells Overview",            "cellapps", "cells/*/*",
	"Information on the cells handled by CellApps." ),

("CellApp Config",           "cellapps", "config/*",
	"Configuration settings for CellApps." ),

("CellApp C++ Profiles",      "cellapps", "profiles/details/*/*",
	"Details for time spent in different parts of the C++ code. This is"
	"useful for identifying where processing time is being taken.<br/>"
	"<i>Note:</i> The timing units are in stamps. "
	"See <i>cellapp/stats/stampsPerSecond</i> watcher value." ),

("CellApp Network Interface", "cellapps", "nub/interfaceByID/*/*",
	"Shows stats for different messages received by CellApps. This is useful "
	"for identifying where bandwidth is being used." ),

("CellApp Network Interface Timing",
			 "cellapps", "nub/interfaceByName/*/timingInSeconds/*",
	"Shows stats for different messages received by CellApps. This is useful "
	"for identifying where bandwidth is being used." ),

# ("CellApp Entities",          "cellapps", "entities/*/*",
#	"Information on all of the CellApp entities. This can generate a lot "
#	"of information and should be used cautiously.<br/>"
#	"<i>Note:</i> This is only practical to use for small, development servers." ),

("CellApp Stats",             "cellapps", "stats/*",
	"General statistics on CellApps." ),

("Entity Types",      "cellapp",  "entityTypes/*/interface/*",
	"Gives a summary of entity definitions." ),

("Entity Properties", "cellapp",  "entityTypes/*/properties/*/*",
	"The properties of all entity definitions. "
	"See <i>Client Methods</i>, <i>CellApp Method Time Taken<i> and "
	"<i>BaseApp Method Time Taken</i> for information on methods." ),

("Client Methods" ,   "cellapp",  "entityTypes/*/methods/clientMethods/*/*",
	"This client methods of all entity definitions." ),


("CellApp Method Calls", "cellapps",
		"entityTypes/*/methods/cellMethods/*/stats/totals/*",
	"Bandwidth information on script method calls for CellApps." ),

("CellApp Method Calls:  1 minute average", "cellapps",
		"entityTypes/*/methods/cellMethods/*/stats/averages/short/*",
	"Bandwidth information on script method calls for CellApps exponentially "
	"averaged over the last minute." ),

("CellApp Method Calls: 10 minute average", "cellapps",
		"entityTypes/*/methods/cellMethods/*/stats/averages/medium/*",
	"Bandwidth information on script method calls for CellApps exponentially "
	"averaged over the last 10 minutes." ),

("CellApp Method Calls: 60 minute average ", "cellapps",
		"entityTypes/*/methods/cellMethods/*/stats/averages/long/*",
	"Bandwidth information on script method calls for CellApps exponentially "
	"averaged over the last 60 minutes." ),

("CellApp Method Time Taken", "cellapps",
		"entityTypes/*/methods/cellMethods/*/*",
	"Number of calls and processing time for script methods called on cell "
	"entities. An <i>exposedIndex</i> of -1 indicates that the method is not "
	"callable from a client.<br/>"
	"<i>Note:</i> The timing units are in stamps. "
	"See <i>cellapp/stats/stampsPerSecond</i> watcher value." ),

("CellApp Script Bandwidth", "cellapps",
		"entityTypes/*/stats/all/totals/*",
	"The bandwidth sent and received per entity type." ),

("CellApp Script Bandwidth: 1 minute average", "cellapps",
		"entityTypes/*/stats/all/averages/short/*",
	"The bandwidth sent and received per entity type." ),

("CellApp Script Bandwidth: 10 minute average", "cellapps",
		"entityTypes/*/stats/all/averages/medium/*",
	"The bandwidth sent and received per entity type." ),

("CellApp Script Bandwidth: 60 minute average", "cellapps",
		"entityTypes/*/stats/all/averages/long/*",
	"The bandwidth sent and received per entity type." ),

("CellApp Property Changes", "cellapps",
		"entityTypes/*/properties/*/stats/totals/*",
	"Information on bandwidth caused by changes to entity properties.>" ),

("CellApp Property Changes: 1 minute average", "cellapps",
		"entityTypes/*/properties/*/stats/averages/short/*",
	"Information on bandwidth caused by changes to entity properties." ),

("CellApp Property Changes: 10 minute average", "cellapps",
		"entityTypes/*/properties/*/stats/averages/medium/*",
	"Information on bandwidth caused by changes to entity properties." ),

("CellApp Property Changes: 60 minute average", "cellapps",
		"entityTypes/*/properties/*/stats/averages/long/*",
	"Information on bandwidth caused by changes to entity properties." ),

# CellAppMgr Filters
("CellAppMgr Channels", "cellappmgr", "cellApps/*/channel/*",
	"The network channels from the CellAppMgr to the CellApps." ),

("CellAppMgr Apps",     "cellappmgr", "cellApps/*/*",
	"The CellAppMgr's view of the CellApps." ),

("CellAppMgr Spaces",     "cellappmgr", "spaces/*/*",
	"The CellAppMgr's view of the Spaces." ),

# BaseApp Filters
("BaseApp Config",           "baseapps", "config/*",
	"Configuration settings for BaseApps." ),

("BaseApp To Manager",             "baseapps", "baseAppMgr/*",
	"Information on the channels from BaseApp to the BaseAppMgr." ),

("BaseApp Logins",                 "baseapps", "logins/*",
	"Information on the number of logins to each BaseApp." ),

("BaseApp Network Internal Interface",      "baseapps", "nub/interfaceByID/*/*",
	"Shows stats for different messages received by the internal network "
	"interface of BaseApps. This is useful for identifying what network "
	"traffic is being sent from other server processes." ),

("BaseApp Network Internal Interface Timing",
 				"baseapps", "nub/interfaceByName/*/timingInSeconds/*",
	"Shows timing stats for different messages received by the internal network "
	"interface of BaseApps. This is useful for identifying were time is being "
	"spent." ),

("BaseApp Network External Interface", "baseapps",
		"nubExternal/interfaceByID/*/*",
	"Shows stats for different messages received by the external network "
	"interface of BaseApps. This is useful for identifying what network "
	"traffic is being sent from Client Apps." ),

("BaseApp Network External Interface Timing",
				"baseapps", "nubExternal/interfaceByName/*/timingInSeconds/*",
	"Shows timing stats for different messages received by the external network "
	"interface of BaseApps. This is useful for identifying were time is being "
	"spent." ),

# ("BaseApp Entities",               "baseapps", "entities/*/*",
#	"Some details about all of the BaseApp entities.<br/>"
#	"<ul>"
#	"<li><i>backupSize</i> - bytes required to back up a base entity to another BaseApp.</li>"
#	"<li><i>databaseResidentSize</i> - bytes required to back up to disk.</li>"
#	"</ul>"
#	"<i>Note:</i> This is only practical to use for small, development servers."
#	),

("BaseApp Stats",             "baseapps", "stats/*",
	"General statistics on BaseApps." ),

("BaseApp Method Calls",   "baseapps",
		"entityTypes/*/methods/baseMethods/*/stats/totals/*",
	"Bandwidth information on script method calls from BaseApps." ),

("BaseApp Method Calls: 1 minute average",   "baseapps",
		"entityTypes/*/methods/baseMethods/*/stats/averages/short/*",
	"Bandwidth information on script method calls from BaseApps." ),

("BaseApp Method Calls: 10 minute average",   "baseapps",
		"entityTypes/*/methods/baseMethods/*/stats/averages/medium/*",
	"Bandwidth information on script method calls from BaseApps." ),

("BaseApp Method Calls: 60 minute average",   "baseapps",
		"entityTypes/*/methods/baseMethods/*/stats/averages/long/*",
	"Bandwidth information on script method calls from BaseApps." ),

("BaseApp Method Time Taken",      "baseapps",
		"entityTypes/*/methods/baseMethods/*/*",
	"Number of calls and processing time for script methods called on base "
	"entities. An <i>exposedIndex</i> of -1 indicates that the method is not "
	"callable from a client.<br/>"
	"<i>Note:</i> The timing units are in stamps. "
	"See <i>baseapp/stats/stampsPerSecond</i> watcher value." ),

("DBApp Entity Writes", "dbapps",
	"profiles/details/writeEntity/count",
	"The counts of entity writes across all DBApps."),

("Versions", "all", "version/*",
	"The version of BigWorld." ),

("Addresses", "all", "nub/address",
	"The address of the internal network socket for all processes." ),

("Network Sending",   "all", "nub/sending/stats/averages/long/*",
	"Bandwidth information on quantity sent by each process." ),

("Network Receiving", "all", "nub/receiving/stats/averages/long/*",
	"Bandwidth information on quantity received by each process." ),

	# BaseAppMgr Filters
("BaseAppMgr Channels", "baseappmgr", "baseApps/*/internalChannel/*",
	"The network channels from the BaseAppMgr to the BaseApps." ),

("BaseAppMgr Apps", "baseappmgr", "baseApps/*/*",
	"The BaseAppMgr's view of the BaseApps." ),

)

WATCHER_FILTERS = [dict( zip( ("name", "processes", "path", "description"), args ) )
				for args in ARGS]

WATCHER_FILTERS.sort( lambda x, y : cmp( x[ "name" ], y[ "name" ] ) )

def hasWatcherFilter( name ):
	for filter in WATCHER_FILTERS:
		if filter[ "name" ] == name:
			return True

	return False

# preconfigured.py
