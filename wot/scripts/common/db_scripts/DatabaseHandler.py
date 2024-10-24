import cPickle
import pprint
import zlib
from itertools import cycle
import os
import ast

import BigWorld
import oursql

import AccountCommands
import bwdebug
import ResMgr

import BackgroundTask
import items
import nations
from adisp import async, process
from bwdebug import TRACE_MSG, DEBUG_MSG
from constants import ACCOUNT_ATTR, EVENT_CLIENT_DATA
from items import vehicles, ITEM_TYPE_INDICES

threadManager = None

""" TODO: Implement the following classes
UniversalBackgroundDatabaseHandler.QuestsHandler
UniversalBackgroundDatabaseHandler.InventoryHandler
UniversalBackgroundDatabaseHandler.StatsHandler
UniversalBackgroundDatabaseHandler.DossierHandler
"""

def init():
	global threadManager
	if threadManager is None:
		threadManager = BackgroundTask.Manager("DatabaseHandler")
		threadManager.startThreads(15)
		TRACE_MSG('DatabaseHandler :: Initialized background thread manager.')
	return True

def fini():
	global threadManager
	if threadManager is not None:
		threadManager.stopAll()
		threadManager = None
		TRACE_MSG('DatabaseHandler :: Stopped background thread manager.')

def add_task(task):
	if threadManager is None:
		assert threadManager is None, "DatabaseHandler :: Background thread manager is not initialized. Has it been initialized in the personality script?"
		raise RuntimeError("UniversalBackgroundDatabaseHandler is not initialized.")
	threadManager.addBackgroundTask(task)

# #

def press_unlocked_veh_co_de():
	"""
	# PRESS ACCOUNTS ONLY #
	Universal function to define tanks that are unlocked AND added to first time press account garages. Any tank can be
	added here by appending its compact description below the for-loop, or, by modifying the for-loop directly.
	@return: set
	"""
	unlocked_veh_co_de = set()
	for nationID in nations.INDICES.values():
		unlocked_veh_co_de |= {vehicle['compactDescr'] for vehicle in vehicles.g_list.getList(nationID).values() if 'premiumIGR' not in vehicle.get('tags')}
	
	return unlocked_veh_co_de

def unlocked_veh_co_de(for_stats=True):
	"""
	Universal function to define tanks that are unlocked AND added to first time players' garages. Any tank can be
	added here by appending its compact description below the for-loop, or, by modifying the for-loop directly.
	@return: set
	"""
	if for_stats:
		unlocked_veh_co_de = set()
		for nationID in nations.INDICES.values():
			unlocked_veh_co_de |= {vehicle['compactDescr'] for vehicle in vehicles.g_list.getList(nationID).values() if vehicle.get('level') == 1 and 'secret' not in vehicle.get('tags') and 'premiumIGR' not in vehicle.get('tags')}
		unlocked_veh_co_de |= {52513}   # M6 mutant
		unlocked_veh_co_de |= {54033}   # pz v/iv alpha
		# unlocked_veh_co_de |= {55633}   # cromwell b
		
		# addition of premium tanks, as they require zero xp to buy, so they need to be here, unlocked, regardless of whether they are in the shop or not
		unlocked_veh_co_de |= {52505, 51985, 51489, 2113, 53585, 49, 3169, 52481, 54801, 52769, 2369, 53841, 305, 52065,
		                       51457, 54545, 13345, 63297, 54097, 817, 51553, 51713, 57105, 2849, 63553, 54353, 64049,
		                       51809, 54785, 57361, 33, 63809, 54609, 64561, 55297, 55313, 11809, 64065, 54865, 64817, 9217,
		                       60177, 12577, 55121, 51201, 51473, 15905, 55633, 52225, 51729, 51745, 55889, 52737, 52241,
		                       52001, 52993, 52497, 52257, 53249, 54033, 52513, 53761, 54289, 53537, 54017, 55057, 53793,
		                       54273, 55569, 54049, 56577, 57105, 55073, 56833, 57617, 55841, 57089, 58641, 56097, 58113,
		                       59665, 56353, 58369, 60433, 56609, 58625, 60689, 58881, 60945, 59137, 61201, 59393, 61457,
		                       59649, 61713, 59905, 60161, 53505}
		
		return unlocked_veh_co_de
	else:
		unlocked_veh_co_de = set()
		for nationID in nations.INDICES.values():
			unlocked_veh_co_de |= {vehicle['compactDescr'] for vehicle in vehicles.g_list.getList(nationID).values()
			                       if vehicle.get('level') == 1 and 'secret' not in vehicle.get('tags')
			                       and 'premiumIGR' not in vehicle.get('tags')}
		unlocked_veh_co_de |= {52513}  # M6 mutant
		unlocked_veh_co_de |= {54033}  # pz v/iv alpha
		# unlocked_veh_co_de |= {55633}  # cromwell b
		
		return unlocked_veh_co_de

def initEmptyQuests():
	DEBUG_MSG('DatabaseWorker : initEmptyQuests')
	rdata = {
		'tokens': {'count': 0, 'expiryTime': 0},
		'potapovQuests': {'compDescr': '', 'slots': 0, 'selected': [], 'rewards': {}, 'unlocked': {}},
		'quests': {'progress': 0}
	}
	return rdata
	
def initEmptyInventory():
	DEBUG_MSG('DatabaseWorker : initEmptyInventory')
	unlocked_vehs = unlocked_veh_co_de(for_stats=False)
	
	data = dict((k, {}) for k in ITEM_TYPE_INDICES)
	i = 1
	i_crew = 1
	compDescr = {}
	data[ITEM_TYPE_INDICES['vehicle']] = {
		'repair': {},
		'lastCrew': {},
		'crew': {},
		'settings': {},
		'compDescr': {},
		'eqs': {},
		'eqsLayout': {},
		'shells': {},
		'customizationExpiryTime': {},
		'lock': {},
		'shellsLayout': {}
	}

	data[ITEM_TYPE_INDICES['tankman']] = {
		'vehicle': {},
		'compDescr': {}
	}
	
	# data[ITEM_TYPE_INDICES['equipment']] = {}
	# data[ITEM_TYPE_INDICES['optionalDevice']] = {}
	# data[ITEM_TYPE_INDICES['shell']] = {}
	# data[ITEM_TYPE_INDICES['vehicleChassis']] = {}
	# data[ITEM_TYPE_INDICES['vehicleEngine']] = {}
	# data[ITEM_TYPE_INDICES['vehicleFuelTank']] = {}
	# data[ITEM_TYPE_INDICES['vehicleGun']] = {}
	# data[ITEM_TYPE_INDICES['vehicleRadio']] = {}
	# data[ITEM_TYPE_INDICES['vehicleTurret']] = {}

	for value in unlocked_vehs: # vehicles.g_list._VehicleList__ids.values()
		value = vehicles.getVehicleType(value).id
		vehicle = vehicles.VehicleDescr(typeID=value)
		# components can be installed at this step
		compDescr[i] = vehicle.makeCompactDescr()
		turretGun = (vehicles.makeIntCompactDescrByID('vehicleTurret', *vehicle.turrets[0][0]['id']), vehicles.makeIntCompactDescrByID('vehicleGun', *vehicle.turrets[0][0]['guns'][0]['id']))

		tmanList = items.tankmen.generateTankmen(value[0], value[1], vehicle.type.crewRoles, True, items.tankmen.MAX_SKILL_LEVEL, [])
		tmanListCycle = cycle(tmanList)

		data[ITEM_TYPE_INDICES['vehicle']]['crew'].update({i: [tmanID for tmanID in xrange(i_crew, len(tmanList) + i_crew)]})
		data[ITEM_TYPE_INDICES['vehicle']]['settings'].update({i: AccountCommands.VEHICLE_SETTINGS_FLAG.AUTO_REPAIR | AccountCommands.VEHICLE_SETTINGS_FLAG.AUTO_LOAD})
		data[ITEM_TYPE_INDICES['vehicle']]['compDescr'].update(compDescr)
		data[ITEM_TYPE_INDICES['vehicle']]['eqs'].update({i: []})
		data[ITEM_TYPE_INDICES['vehicle']]['eqsLayout'].update({i: []})
		# data[ITEM_TYPE_INDICES['vehicle']]['shells'].update({i: vehicles.getDefaultAmmoForGun(vehicle.turrets[0][0]['guns'][0])})
		data[ITEM_TYPE_INDICES['vehicle']]['shellsLayout'].update({i: {turretGun: vehicles.getDefaultAmmoForGun(vehicle.turrets[0][0]['guns'][0])}})

		for tmanID in xrange(i_crew, len(tmanList) + i_crew):
			data[ITEM_TYPE_INDICES['tankman']]['vehicle'][tmanID] = i
			data[ITEM_TYPE_INDICES['tankman']]['compDescr'][tmanID] = next(tmanListCycle)
			i_crew += 1

		i += 1
	
	rdata = {'inventory': data}
	
	return rdata

def initEmptyStats():
	DEBUG_MSG('DatabaseHandler : initEmptyStats')
	unlocked_vehs = unlocked_veh_co_de(for_stats=True)
	
	unlocksSet = set()
	vehiclesSet = set()
	
	eliteVehicles = {52513, 54033}
	
	# TODO: use for inventory and shit adder thingy in webconsole
	# pz_viv = vehicles.getVehicleType(54033)
	# pz_viv = vehicles.VehicleDescr(typeID=pz_viv.id)
	# print pz_viv.getComponentsByType('vehicleGun')[1]
	for veh_cd in unlocked_vehs:
		nation_id, veh_id = vehicles.getVehicleType(veh_cd).id
		turret = vehicles.g_cache.vehicle(nation_id, veh_id).turrets[0][0]
		turret_nid, turret_id = turret['id']
		gun = turret['guns'][0]
		gun_nid, gun_id = gun['id']
		
		unlocksSet.add(vehicles.g_cache.vehicle(nation_id, veh_id).chassis[0]['compactDescr'])
		unlocksSet.add(vehicles.g_cache.vehicle(nation_id, veh_id).engines[0]['compactDescr'])
		unlocksSet.add(vehicles.g_cache.vehicle(nation_id, veh_id).fuelTanks[0]['compactDescr'])
		unlocksSet.add(vehicles.g_cache.vehicle(nation_id, veh_id).radios[0]['compactDescr'])
		
		
		unlocksSet.add(vehicles.makeIntCompactDescrByID('vehicleTurret', turret_nid, turret_id))
		unlocksSet.add(vehicles.makeIntCompactDescrByID('vehicleGun', gun_nid, gun_id))
	
	unlocksSet |= unlocked_vehs
	vehiclesSet |= unlocked_vehs
	
	for nationID in nations.INDICES.values():
		unlocksSet |= {vehicles.makeIntCompactDescrByID('shell', nationID, i) for i in
		               vehicles.g_cache.shells(nationID).keys()}
		# unlocked_veh_co_de = {vehicles.makeIntCompactDescrByID('vehicle', nationID, i) for i in vehicles.g_list.getList(nationID).keys()}
		# unlocked_veh_co_de = {vehicle['compactDescr'] for vehicle in vehicles.g_list.getList(nationID).values() if vehicle.get('level') == 1 and 'secret' not in vehicle.get('tags')}
	
	# amount of XP avail for each unlocked vehicle
	vehTypeXP = {i: 0 for i in vehiclesSet if i not in {52505, 51985, 51489, 2113, 53585, 49, 3169, 52481, 54801, 52769, 2369, 53841, 305, 52065,
		                       51457, 54545, 13345, 63297, 54097, 817, 51553, 51713, 57105, 2849, 63553, 54353, 64049,
		                       51809, 54785, 57361, 33, 63809, 54609, 64561, 55297, 55313, 11809, 64065, 54865, 64817, 9217,
		                       60177, 12577, 55121, 51201, 51473, 15905, 55633, 52225, 51729, 51745, 55889, 52737, 52241,
		                       52001, 52993, 52497, 52257, 53249, 54033, 52513, 53761, 54289, 53537, 54017, 55057, 53793,
		                       54273, 55569, 54049, 56577, 57105, 55073, 56833, 57617, 55841, 57089, 58641, 56097, 58113,
		                       59665, 56353, 58369, 60433, 56609, 58625, 60689, 58881, 60945, 59137, 61201, 59393, 61457,
		                       59649, 61713, 59905, 60161}}
	vehTypeXP[52513] = 5000000
	vehTypeXP[54033] = 5000000
	
	attrs = 0
	excluded_attrs = (ACCOUNT_ATTR.PREMIUM, ACCOUNT_ATTR.OUT_OF_SESSION_WALLET, ACCOUNT_ATTR.CBETA,
	                  ACCOUNT_ATTR.OBETA, ACCOUNT_ATTR.AOGAS, ACCOUNT_ATTR.TUTORIAL_COMPLETED,
	                  ACCOUNT_ATTR.IGR_PREMIUM, ACCOUNT_ATTR.IGR_BASE, ACCOUNT_ATTR.ALPHA, ACCOUNT_ATTR.CLAN, ACCOUNT_ATTR.TRADING)
	for field in dir(ACCOUNT_ATTR):
		value = getattr(ACCOUNT_ATTR, field, None)
		if isinstance(value, (int, long)) and value not in excluded_attrs:
			attrs |= value
	
	rdata = {
		'stats': {
			'crystalExchangeRate': 200,
			'applyAdditionalXPCount': 1,
			'accOnline': 200,
			'berths': 40,
			'credits': 10000000,
			'gold': 100000,
			'crystal': 1000,
			'freeXP': 100000,
			'finPswdAttemptsLeft': 9999,
			'denunciationsLeft': 10,
			'freeVehiclesLeft': 2,
			'refSystem': {'referrals': {}},
			'slots': 10,
			'battlesTillCaptcha': 9999999,
			'hasFinPassword': False,
			'freeTMenLeft': 25,
			'vehicleSellsLeft': 25,
			'SPA': {'/common/goldfish_bonus_applied/': u'1'},
			'vehTypeXP': vehTypeXP,
			'globalVehicleLocks': {},
			'captchaTriesLeft': 999,
			'fortResource': 0,
			'tkillIsSuspected': False,
			'vehTypeLocks': {},
			'dailyPlayHours': [889, 0, 2172, 1045, 1933, 5881, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			'restrictions': {},
			'oldVehInvID': 0,
			'accOffline': 75,
			'dossier': '',
			'multipliedXPVehs': [],
			'tutorialsCompleted': 33553532,
			'playLimits': ((0, ''), (0, '')),  # ((86400, ''), (604800, ''))
			'maxResearchedLevelByNation': {"0": 1, "1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "6": 1},
			'unlocks': unlocksSet,
			'eliteVehicles': set()
		},
		'account': {
			'clanDBID': 0,
			'premiumExpiryTime': 0,
			'autoBanTime': 0,
			'globalRating': 4500,
			'attrs': attrs
		},
		'cache': {
			'isFinPswdVerified': True,
			'mayConsumeWalletResources': True,
			'unitAcceptDeadline': 0,
			'vehsLock': {},
			'relatedToClubs': {},
			'cybersportSeasonInProgress': {},
			'clanFortState': None
		},
		'economics': {
			'unlocks': set(),
			'eliteVehicles': eliteVehicles,  # vehiclesSet
		},
		'offers': {
			'in': {'offer1': {'item': 'sword', 'price': 100}, 'offer2': {'item': 'shield', 'price': 150}},
			'out': {'offer3': {'item': 'bow', 'price': 100}, 'offer2': None}
		},
		('intUserSettings', '_r'): {0: 13, 1: 1342422138, 2: 1, 3: 0, 4: 0, 5: 17, 6: 31, 7: 30, 8: 32, 9: 45,
		                            10: 19, 11: 33, 12: 0, 13: 256, 14: 257, 15: 18, 16: 42, 17: 46, 18: 47, 19: 44,
		                            20: 2, 21: 3, 22: 4, 23: 5, 24: 6, 25: 7, 26: 8, 27: 9, 28: 20, 29: 62, 30: 63,
		                            31: 64, 32: 65, 33: 66, 34: 200, 35: 208, 36: 203, 37: 205, 38: 16, 39: 210,
		                            40: 13, 41: 12, 42: 50, 43: 6554368, 44: 6553600, 45: 1677747300, 46: 6554368,
		                            47: 6553600, 48: 1677747300, 49: 40763742, 50: 50331932, 51: 36569374,
		                            52: 1494220809, 53: 1140916717, 54: 42, 55: 67, 57: 553, 58: 15, 59: 789330893,
		                            61: 160207, 62: 0, 63: 100, 64: 100, 65: 81, 68: 2, 69: 41, 70: 1073705470,
		                            71: 89, 73: 536870912, 74: 128, 77: 0, 79: 801, 80: 0, 81: 1668, 82: 79,
		                            83: 271, 84: 143093, 85: 0, 86: 2125331343, 87: 134217728, 88: 128, 90: 5,
		                            91: 0, 92: 0, 93: 0, 94: 0, 95: 0, 96: 135576, 97: 1717963694, 98: 31522819,
		                            99: 2068443135, 100: 229376, 101: 644, 102: 57, 103: 0, 105: 33528791, 106: 51,
		                            107: 536870912, 108: 512, 109: 891, 110: 536870912, 111: 644, 112: 3, 114: 3,
		                            115: 3, 31001: 51815706, 31002: 536870912, 31003: 132, 500: 0},
		('eventsData', '_r'): {
			EVENT_CLIENT_DATA.NOTIFICATIONS: [
				{'id': 1, 'message': 'Event 1', 'timestamp': 1633036800, 'type': '', 'data': {}},
				{'id': 2, 'message': 'Event 2', 'timestamp': 1633123200, 'type': '', 'data': {}},
			],
			EVENT_CLIENT_DATA.NOTIFICATIONS_REV: 1
		}
	}
	
	return rdata

def initEmptyDossier():
	DEBUG_MSG('DatabaseHandler : initEmptyDossier')
	rdata = {(12345, 1622547800, 'dossierCompDescr1'), (67890, 1622547900, 'dossierCompDescr2'),
	         (13579, 1622548000, 'dossierCompDescr3')}
	return rdata

# #

class GetFullSyncData(BackgroundTask.BackgroundTask):
	"""
	Queries the player database for all data related to first-time client sync (syncData).
	"""
	def __init__(self, databaseID, callback):
		self.databaseID = databaseID
		self.callback = callback
		self.result = None  # dict
		self.quests_path = None
		self.inventory_path = None
		self.stats_path = None
	
	def doBackgroundTask(self, bgTaskMgr, threadData):
		TRACE_MSG('GetFullSyncData (background) :: databaseID=%s' % self.databaseID)
		self.quests_path = ResMgr.resolveToAbsolutePath('server/database_files/quests/')
		self.inventory_path = ResMgr.resolveToAbsolutePath('server/database_files/inventory/')
		self.stats_path = ResMgr.resolveToAbsolutePath('server/database_files/stats/')
		paths = [self.quests_path, self.inventory_path, self.stats_path]
		for f in paths:
			if not os.path.exists(f):
				os.makedirs(f)
		self.result = {}
		
		quests_file = os.path.join(self.quests_path, "%s" % self.databaseID)
		if not os.path.isfile(quests_file):
			self.result.update(initEmptyQuests())  # dict
			
			try:
				with open(quests_file, 'wb') as file:
					pprint.pprint(initEmptyQuests(), stream=file)
			except Exception as e:
				raise Exception("GetFullSyncData :: Error occurred while writing quests data (init)=%s" % e)
		else:
			try:
				with open(quests_file, 'rb') as file:
					foo = file.read()  # str
				self.result.update(eval(foo))  # dict
			except Exception as e:
				raise Exception("GetFullSyncData :: Error occurred while fetching quests data=%s" % e)
		
		inventory_file = os.path.join(self.inventory_path, "%s" % self.databaseID)
		if not os.path.isfile(inventory_file):
			self.result.update(initEmptyInventory())  # dict
			
			try:
				with open(inventory_file, 'wb') as file:
					pprint.pprint(initEmptyInventory(), stream=file)
			except Exception as e:
				raise Exception("GetFullSyncData :: Error occurred while writing inventory data (init)=%s" % e)
		else:
			try:
				with open(inventory_file, 'rb') as file:
					foo = file.read()  # str
				self.result.update(eval(foo))  # dict
			except Exception as e:
				raise Exception("GetFullSyncData :: Error occurred while fetching inventory data=%s" % e)
		
		stats_file = os.path.join(self.stats_path, "%s" % self.databaseID)
		if not os.path.isfile(stats_file):
			self.result.update(initEmptyStats())  # dict
			self.result[('eventsData', '_r')][9] = zlib.compress(cPickle.dumps(self.result[('eventsData', '_r')][9]))
			try:
				with open(stats_file, 'wb') as file:
					pprint.pprint(initEmptyStats(), stream=file)
			except Exception as e:
				raise Exception("GetFullSyncData :: Error occurred while writing stats data (init)=%s" % e)
		else:
			try:
				with open(stats_file, 'rb') as file:
					self.result.update(eval(file.read()))  # dict
				self.result[('eventsData', '_r')][9] = zlib.compress(cPickle.dumps(self.result[('eventsData', '_r')][9]))
			except Exception as e:
				raise Exception("GetFullSyncData :: Error occurred while fetching stats data=%s" % e)
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		# TRACE_MSG('GetFullSyncData (foreground) :: databaseID=%s' % self.databaseID)
		self.callback(self.result)


class GetQuestsData(BackgroundTask.BackgroundTask):
	"""
	Queries the database for quest data using.
	"""
	def __init__(self, databaseID, callback):
		self.databaseID = databaseID
		self.callback = callback
		self.result = None
		self.filepath = None
	
	def doBackgroundTask(self, bgTaskMgr, threadData):
		# TRACE_MSG('GetQuestsData (background) :: databaseID=%s' % self.databaseID)
		self.filepath = ResMgr.resolveToAbsolutePath('server/database_files/quests/')
		if not os.path.exists(self.filepath):
			os.makedirs(self.filepath)
		filename = os.path.join(self.filepath, "%s" % self.databaseID)  # bit weedy, innit
		if not os.path.isfile(filename):
			self.result = self.__initEmptyQuests()  # dict
			
			try:
				with open(filename, 'wb') as file:
					pprint.pprint(self.result, stream=file)
			except Exception as e:
				raise Exception("GetQuestsData :: Error occurred while writing inventory data (init)=%s" % e)
		else:
			try:
				with open(filename, 'rb') as file:
					self.result = file.read()  # str
				self.result = eval(self.result)  # dict
			except Exception as e:
				raise Exception("GetQuestsData :: Error occurred while fetching inventory data=%s" % e)
		bgTaskMgr.addMainThreadTask(self)
	
	def __initEmptyQuests(self):
		return initEmptyQuests()
	
	def doMainThreadTask(self, bgTaskMgr):
		# TRACE_MSG('GetQuestsData (foreground) :: databaseID=%s' % self.databaseID)
		self.callback(self.result)

class GetQuestsDataKeyed(BackgroundTask.BackgroundTask):
	"""
	Queries the database for quest data and returns the data keyed by the specified key.
	"""
	pass

class UpdateQuestsData(BackgroundTask.BackgroundTask):
	"""
	Updates the quests data in the database.
	"""
	pass


class GetInventoryData(BackgroundTask.BackgroundTask):
	"""
	Queries the database for inventory data.
	"""
	def __init__(self, databaseID, callback):
		self.databaseID = databaseID
		self.callback = callback
		self.result = None
		self.filepath = None
	
	def doBackgroundTask(self, bgTaskMgr, threadData):
		# TRACE_MSG('GetInventoryData (background) :: databaseID=%s' % self.databaseID)
		self.filepath = ResMgr.resolveToAbsolutePath('server/database_files/inventory/')
		if not os.path.exists(self.filepath):
			os.makedirs(self.filepath)
		filename = os.path.join(self.filepath, "%s" % self.databaseID)
		if not os.path.isfile(filename):
			self.result = self.__initEmptyInventory()   # dict
			
			try:
				with open(filename, 'wb') as file:
					pprint.pprint(self.result, stream=file)
			except Exception as e:
				raise Exception("GetInventoryData :: Error occurred while writing inventory data (init)=%s" % e)
		else:
			try:
				with open(filename, 'rb') as file:
					self.result = file.read()   # str
				self.result = eval(self.result)  # dict
			except Exception as e:
				raise Exception("GetInventoryData :: Error occurred while fetching inventory data=%s" % e)
		bgTaskMgr.addMainThreadTask(self)
	
	def __initEmptyInventory(self):
		return initEmptyInventory()
	
	def doMainThreadTask(self, bgTaskMgr):
		# TRACE_MSG('GetInventoryData (foreground) :: databaseID=%s' % self.databaseID)
		self.callback(self.result)
	
class SetInventoryData(BackgroundTask.BackgroundTask):
	"""
	Updates the inventory data in the database.
	"""
	def __init__(self, databaseID, data, callback):
		self.databaseID = databaseID
		self.data = data
		self.callback = callback
		self.result = None
		self.filepath = None
	
	def doBackgroundTask(self, bgTaskMgr, threadData):
		# TRACE_MSG('SetInventoryData (background) :: databaseID=%s' % self.databaseID)
		self.filepath = ResMgr.resolveToAbsolutePath('server/database_files/inventory/')
		if not os.path.exists(self.filepath):
			os.makedirs(self.filepath)
		filename = os.path.join(self.filepath, "%s" % self.databaseID)
		try:
			with open(filename, 'wb') as file:
				pprint.pprint(self.data, stream=file)
			self.result = True
		except Exception as e:
			raise Exception("SetInventoryData :: Error occurred while writing inventory data=%s" % e)
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		# TRACE_MSG('SetInventoryData (foreground) :: databaseID=%s' % self.databaseID)
		self.callback(self.result)


class GetStatsData(BackgroundTask.BackgroundTask):
	"""
	Queries player database for stats data.
	"""
	def __init__(self, databaseID, callback):
		self.databaseID = databaseID
		self.callback = callback
		self.result = None
		self.filepath = None
	
	def doBackgroundTask(self, bgTaskMgr, threadData):
		# TRACE_MSG('GetStatsData (background) :: databaseID=%s' % self.databaseID)
		self.filepath = ResMgr.resolveToAbsolutePath('server/database_files/stats/')
		if not os.path.exists(self.filepath):
			os.makedirs(self.filepath)
		filename = os.path.join(self.filepath, "%s" % self.databaseID)
		if not os.path.isfile(filename):
			self.result = self.__initEmptyStats()  # dict
			try:
				with open(filename, 'wb') as file:
					pprint.pprint(self.result, stream=file)
				self.result[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS] = zlib.compress(
					cPickle.dumps(self.result[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS]))
			except Exception as e:
				raise Exception("GetStatsData :: Error occurred while writing stats data (init)=%s" % e)
		else:
			try:
				with open(filename, 'rb') as file:
					self.result = file.read()  # str
				self.result = eval(self.result)  # dict
				self.result[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS] = zlib.compress(
					cPickle.dumps(self.result[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS]))
			except Exception as e:
				raise Exception("GetStatsData :: Error occurred while fetching stats data=%s" % e)
		bgTaskMgr.addMainThreadTask(self)
	
	def __initEmptyStats(self):
		return initEmptyStats()
	
	def doMainThreadTask(self, bgTaskMgr):
		# TRACE_MSG('GetStatsData (foreground) :: databaseID=%s' % self.databaseID)
		self.callback(self.result)

class SetStatsData(BackgroundTask.BackgroundTask):
	"""
	Updates stats data in player database.
	"""
	def __init__(self, databaseID, data, callback):
		self.databaseID = databaseID
		self.data = data
		self.callback = callback
		self.result = None
		self.filepath = None
	
	def doBackgroundTask(self, bgTaskMgr, threadData):
		# TRACE_MSG('SetStatsData (background) :: databaseID=%s' % self.databaseID)
		self.filepath = ResMgr.resolveToAbsolutePath('server/database_files/stats/')
		if not os.path.exists(self.filepath):
			os.makedirs(self.filepath)
		filename = os.path.join(self.filepath, "%s" % self.databaseID)
		self.data[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS] = cPickle.loads(zlib.decompress(self.data[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS]))
		try:
			with open(filename, 'wb') as file:
				pprint.pprint(self.data, stream=file)
			self.result = True
		except Exception as e:
			raise Exception("SetStatsData :: Error occurred while writing stats data=%s" % e)
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		# TRACE_MSG('SetStatsData (foreground) :: databaseID=%s' % self.databaseID)
		self.callback(self.result)


class GetDossierData(BackgroundTask.BackgroundTask):
	"""
	Queries player database for stats data.
	"""
	
	def __init__(self, databaseID, callback):
		self.databaseID = databaseID
		self.callback = callback
		self.result = None
		self.filepath = None
	
	def doBackgroundTask(self, bgTaskMgr, threadData):
		TRACE_MSG('GetDossierData (background) :: databaseID=%s' % self.databaseID)
		self.filepath = ResMgr.resolveToAbsolutePath('server/database_files/dossier/')
		if not os.path.exists(self.filepath):
			os.makedirs(self.filepath)
		filename = os.path.join(self.filepath, "%s" % self.databaseID)
		if not os.path.isfile(filename):
			self.result = self.__initEmptyDossier()  # dict
			
			try:
				with open(filename, 'wb') as file:
					pprint.pprint(self.result, stream=file)
			except Exception as e:
				raise Exception("GetDossierData :: Error occurred while writing stats data (init)=%s" % e)
		else:
			try:
				with open(filename, 'rb') as file:
					self.result = file.read()  # str
				self.result = eval(self.result)  # dict
			except Exception as e:
				raise Exception("GetDossierData :: Error occurred while fetching stats data=%s" % e)
		bgTaskMgr.addMainThreadTask(self)
	
	def __initEmptyDossier(self):
		return initEmptyDossier()
	
	def doMainThreadTask(self, bgTaskMgr):
		TRACE_MSG('GetDossierData (foreground) :: databaseID=%s' % self.databaseID)
		self.callback(self.result)