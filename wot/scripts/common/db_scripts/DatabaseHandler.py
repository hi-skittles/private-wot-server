import zlib, os, cPickle, base64, time, pprint, functools
from itertools import cycle

import mysql.connector

import AccountCommands
from bwdebug import INFO_MSG, TRACE_MSG, DEBUG_MSG, WARNING_MSG
import ResMgr, BackgroundTask
from server_constants import DATABASE_CONST
import items, nations
from constants import ACCOUNT_ATTR, EVENT_CLIENT_DATA
from items import vehicles, ITEM_TYPE_INDICES

threadManager = None  # never manually change this value
DATABASE_NAME = DATABASE_CONST.DB_PRIMARY_DATABASE_NAME
DO_DEBUG = DATABASE_CONST.DB_DO_EXTRA_DEBUG


def init():
	connection = mysql.connector.connect(
		host='localhost',
		user='bigworld',
		password='bigworld',
		database=DATABASE_NAME
	)
	if connection.is_connected(): INFO_MSG("[DatabaseHandler] connected to %s" % connection.server_host)
	
	try:
		connection.cursor(buffered=True).execute("""SELECT * FROM inventory LIMIT 1""")
	except mysql.connector.errors.Error:
		WARNING_MSG("[DatabaseHandler] Inventory table does not exist. Creating...")
		connection.cursor(buffered=True).execute(
			"""CREATE TABLE IF NOT EXISTS inventory (email VARCHAR(255) PRIMARY KEY UNIQUE NOT NULL,
			`%s` LONGBLOB, `%s` LONGBLOB, `%s` LONGBLOB, `%s` LONGBLOB, `%s` LONGBLOB, `%s` LONGBLOB, `%s` LONGBLOB, `%s` LONGBLOB, `%s` LONGBLOB, `%s` LONGBLOB, `%s` LONGBLOB, updated_at timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP) charset=utf8""",
			(ITEM_TYPE_INDICES['vehicle'], ITEM_TYPE_INDICES['vehicleChassis'], ITEM_TYPE_INDICES['vehicleTurret'],
			 ITEM_TYPE_INDICES['vehicleGun'], ITEM_TYPE_INDICES['vehicleEngine'], ITEM_TYPE_INDICES['vehicleFuelTank'],
			 ITEM_TYPE_INDICES['vehicleRadio'], ITEM_TYPE_INDICES['tankman'], ITEM_TYPE_INDICES['optionalDevice'],
			 ITEM_TYPE_INDICES['shell'], ITEM_TYPE_INDICES['equipment']))
	finally:
		connection.commit()
	
	global threadManager
	if threadManager is None:
		threadManager = BackgroundTask.Manager("DatabaseHandler")
		connection_creator = functools.partial(mysql.connector.connect,
		                                       host='localhost',
		                                       user='bigworld',
		                                       password='bigworld',
		                                       database=DATABASE_NAME)
		threadManager.startThreads(5, connection_creator)
		INFO_MSG('[DatabaseHandler] initialized background thread manager.')
	return True


def fini():
	global threadManager
	if threadManager is not None:
		threadManager.stopAll()
		threadManager = None
		WARNING_MSG('[DatabaseHandler] Stopped background thread manager. (called by fini())')


def add_task(task):
	if threadManager is None:
		assert threadManager is None, "[DatabaseHandler] Background thread manager is not initialized. Has it been initialized in the personality script?"
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
		unlocked_veh_co_de |= {vehicle['compactDescr'] for vehicle in vehicles.g_list.getList(nationID).values() if
		                       'premiumIGR' not in vehicle.get('tags')}
	
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
			unlocked_veh_co_de |= {vehicle['compactDescr'] for vehicle in vehicles.g_list.getList(nationID).values() if
			                       vehicle.get('level') == 1 and 'secret' not in vehicle.get(
				                       'tags') and 'premiumIGR' not in vehicle.get('tags')}
		unlocked_veh_co_de |= {52513}  # M6 mutant
		unlocked_veh_co_de |= {54033}  # pz v/iv alpha
		# unlocked_veh_co_de |= {55633}   # cromwell b
		
		# addition of premium tanks, as they require zero xp to buy, so they need to be here, unlocked, regardless of whether they are in the shop or not
		unlocked_veh_co_de |= {52505, 51985, 51489, 2113, 53585, 49, 3169, 52481, 54801, 52769, 2369, 53841, 305, 52065,
		                       51457, 54545, 13345, 63297, 54097, 817, 51553, 51713, 57105, 2849, 63553, 54353, 64049,
		                       51809, 54785, 57361, 33, 63809, 54609, 64561, 55297, 55313, 11809, 64065, 54865, 64817,
		                       9217,
		                       60177, 12577, 55121, 51201, 51473, 15905, 55633, 52225, 51729, 51745, 55889, 52737,
		                       52241,
		                       52001, 52993, 52497, 52257, 53249, 54033, 52513, 53761, 54289, 53537, 54017, 55057,
		                       53793,
		                       54273, 55569, 54049, 56577, 57105, 55073, 56833, 57617, 55841, 57089, 58641, 56097,
		                       58113,
		                       59665, 56353, 58369, 60433, 56609, 58625, 60689, 58881, 60945, 59137, 61201, 59393,
		                       61457,
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
	if DO_DEBUG: TRACE_MSG('[DatabaseHandler] initEmptyQuests')
	rdata = {
		'tokens': {'count': 0, 'expiryTime': 0},
		'potapovQuests': {'compDescr': '', 'slots': 0, 'selected': [], 'rewards': {}, 'unlocked': {}},
		'quests': {'progress': 0}
	}
	return rdata


def initEmptyInventory():
	if DO_DEBUG: TRACE_MSG('[DatabaseHandler] initEmptyInventory')
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
	
	data[ITEM_TYPE_INDICES['equipment']] = {}
	data[ITEM_TYPE_INDICES['optionalDevice']] = {}
	data[ITEM_TYPE_INDICES['shell']] = {}
	data[ITEM_TYPE_INDICES['vehicleChassis']] = {}
	data[ITEM_TYPE_INDICES['vehicleEngine']] = {}
	data[ITEM_TYPE_INDICES['vehicleFuelTank']] = {}
	data[ITEM_TYPE_INDICES['vehicleGun']] = {}
	data[ITEM_TYPE_INDICES['vehicleRadio']] = {}
	data[ITEM_TYPE_INDICES['vehicleTurret']] = {}
	
	for value in unlocked_vehs:  # vehicles.g_list._VehicleList__ids.values()
		value = vehicles.getVehicleType(value).id
		vehicle = vehicles.VehicleDescr(typeID=value)
		# components can be installed at this step
		compDescr[i] = vehicle.makeCompactDescr()
		turretGun = (vehicles.makeIntCompactDescrByID('vehicleTurret', *vehicle.turrets[0][0]['id']),
		             vehicles.makeIntCompactDescrByID('vehicleGun', *vehicle.turrets[0][0]['guns'][0]['id']))
		
		tmanList = items.tankmen.generateTankmen(value[0], value[1], vehicle.type.crewRoles, True,
		                                         items.tankmen.MAX_SKILL_LEVEL, [])
		tmanListCycle = cycle(tmanList)
		
		data[ITEM_TYPE_INDICES['vehicle']]['crew'].update(
			{i: [tmanID for tmanID in xrange(i_crew, len(tmanList) + i_crew)]})
		data[ITEM_TYPE_INDICES['vehicle']]['settings'].update(
			{i: AccountCommands.VEHICLE_SETTINGS_FLAG.AUTO_REPAIR | AccountCommands.VEHICLE_SETTINGS_FLAG.AUTO_LOAD})
		data[ITEM_TYPE_INDICES['vehicle']]['compDescr'].update(compDescr)
		data[ITEM_TYPE_INDICES['vehicle']]['eqs'].update({i: []})
		data[ITEM_TYPE_INDICES['vehicle']]['eqsLayout'].update({i: []})
		# data[ITEM_TYPE_INDICES['vehicle']]['shells'].update({i: vehicles.getDefaultAmmoForGun(vehicle.turrets[0][0]['guns'][0])})
		data[ITEM_TYPE_INDICES['vehicle']]['shellsLayout'].update(
			{i: {turretGun: vehicles.getDefaultAmmoForGun(vehicle.turrets[0][0]['guns'][0])}})
		
		for tmanID in xrange(i_crew, len(tmanList) + i_crew):
			data[ITEM_TYPE_INDICES['tankman']]['vehicle'][tmanID] = i
			data[ITEM_TYPE_INDICES['tankman']]['compDescr'][tmanID] = next(tmanListCycle)
			i_crew += 1
		
		i += 1
	
	rdata = {'inventory': data}
	
	return rdata


def initEmptyStats():
	if DO_DEBUG: TRACE_MSG('[DatabaseHandler] initEmptyStats')
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
	vehTypeXP = {i: 0 for i in vehiclesSet if
	             i not in {52505, 51985, 51489, 2113, 53585, 49, 3169, 52481, 54801, 52769, 2369, 53841, 305, 52065,
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
	included_attrs = (
		ACCOUNT_ATTR.RANDOM_BATTLES, ACCOUNT_ATTR.TRADING, ACCOUNT_ATTR.USER_INFO, ACCOUNT_ATTR.STATISTICS,
		ACCOUNT_ATTR.CHAT_ADMIN, ACCOUNT_ATTR.ADMIN, ACCOUNT_ATTR.DAILY_MULTIPLIED_XP, ACCOUNT_ATTR.ALPHA,
		ACCOUNT_ATTR.CBETA, ACCOUNT_ATTR.OBETA, ACCOUNT_ATTR.AOGAS)
	for field in dir(ACCOUNT_ATTR):
		value = getattr(ACCOUNT_ATTR, field, None)
		if isinstance(value, (int, long)) and value in included_attrs:
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
			'playLimits': ((86400, '24'), (604800, '168')),  # ((86400, ''), (604800, ''))
			'maxResearchedLevelByNation': {"0": 1, "1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "6": 1},
			'unlocks': unlocksSet,
			'eliteVehicles': set()
		},
		'account': {
			'clanDBID': 0,
			'premiumExpiryTime': 0,
			'autoBanTime': 0,
			'globalRating': 0,
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
	
	rdata[('eventsData', '_r')][9] = zlib.compress(cPickle.dumps(rdata[('eventsData', '_r')][9]))
	return rdata


def initEmptyDossier():
	if DO_DEBUG: TRACE_MSG('[DatabaseHandler] initEmptyDossier')
	rdata = {(12345, 1622547800, 'dossierCompDescr1'), (67890, 1622547900, 'dossierCompDescr2'),
	         (13579, 1622548000, 'dossierCompDescr3')}
	return rdata


# #

class GetQuestsData(BackgroundTask.BackgroundTask):
	"""
	Queries the database for quest data as a background task.
	"""
	
	def __init__(self, normalizedName, callback, columns):
		self.normalizedName = normalizedName
		self.columns = columns
		self.callback = callback
		self.result = {}
	
	def doBackgroundTask(self, bgTaskMgr, connection):
		if DO_DEBUG: DEBUG_MSG(
			'[DatabaseHandler] GetQuestsData (background) :: normalizedName=%s' % self.normalizedName)
		if not self.columns: raise Exception("GetQuestsData :: No columns specified")
		if self.columns != '*' and type(self.columns) == list and len(self.columns) > 0:
			self.columns = ', '.join(self.columns)
		c = connection.cursor(dictionary=True)
		c.execute("""SELECT {} FROM quests WHERE email=%s""".format(self.columns), (self.normalizedName,))
		q_result = c.fetchone()
		if q_result is None:
			self.result.update(initEmptyQuests())  # dict
			try:
				c.execute("""INSERT INTO quests (email, tokens, potapovQuests, quests) VALUES (%s, %s, %s, %s)""", (
					self.normalizedName, base64.b64encode(cPickle.dumps(self.result['tokens'])),
					base64.b64encode(cPickle.dumps(self.result['potapovQuests'])),
					base64.b64encode(cPickle.dumps(self.result['quests']))))
			except Exception as e:
				raise Exception("GetQuestsData :: Error occurred while writing quests data (init)=%s" % e)
		else:
			for k, v in q_result.items():
				self.result.update({str(k): cPickle.loads(base64.b64decode(v))})  # dict
		c.close()
		connection.commit()
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		if DO_DEBUG: DEBUG_MSG(
			'[DatabaseHandler] GetQuestsData (foreground) :: normalizedName=%s' % self.normalizedName)
		self.callback(self.result)


# TODO: implement UpdateQuestsData
class UpdateQuestsData(BackgroundTask.BackgroundTask):
	"""
	Updates the quests data in the database.
	"""
	pass


class GetInventoryData(BackgroundTask.BackgroundTask):
	"""
	Queries the database for inventory data.
	"""
	
	def __init__(self, normalizedName, callback, columns):
		self.normalizedName = normalizedName
		self.columns = columns
		self.callback = callback
		self.result = {'inventory': {}}
	
	def doBackgroundTask(self, bgTaskMgr, connection):
		if DO_DEBUG: DEBUG_MSG(
			'[DatabaseHandler] GetInventoryData (background) :: normalizedName=%s' % self.normalizedName)
		if not self.columns: raise Exception("[DatabaseHandler] GetInventoryData :: No columns specified")
		# since the indices are fucking stupid and integers,
		if self.columns != '*' and type(self.columns) == list and len(self.columns) > 0:
			for i in range(len(self.columns)):
				self.columns[i] = str(self.columns[i])
			self.columns = '`' + '`, `'.join(self.columns) + '`'
		c = connection.cursor(dictionary=True)
		try:
			c.execute("""SELECT {} FROM inventory WHERE email=%s""".format(self.columns), (self.normalizedName,))
		except mysql.connector.errors.Error as e:
			raise Exception("[DatabaseHandler] GetInventoryData :: Error occurred while querying inventory data\n%s" % e)
		i_result = c.fetchone()
		if i_result is None:
			self.result.update(initEmptyInventory())  # dict
			try:
				c.execute(
					"""INSERT INTO inventory (email, `{}`, `{}`, `{}`, `{}`, `{}`, `{}`, `{}`, `{}`, `{}`, `{}`, `{}`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""".format(
						ITEM_TYPE_INDICES['vehicle'], ITEM_TYPE_INDICES['vehicleChassis'],
						ITEM_TYPE_INDICES['vehicleTurret'], ITEM_TYPE_INDICES['vehicleGun'],
						ITEM_TYPE_INDICES['vehicleEngine'], ITEM_TYPE_INDICES['vehicleFuelTank'],
						ITEM_TYPE_INDICES['vehicleRadio'], ITEM_TYPE_INDICES['tankman'],
						ITEM_TYPE_INDICES['optionalDevice'], ITEM_TYPE_INDICES['shell'], ITEM_TYPE_INDICES['equipment']
					),
					(
						self.normalizedName,
						base64.b64encode(cPickle.dumps(self.result['inventory'][ITEM_TYPE_INDICES['vehicle']])),
						base64.b64encode(cPickle.dumps({})),
						base64.b64encode(cPickle.dumps({})),
						base64.b64encode(cPickle.dumps({})),
						base64.b64encode(cPickle.dumps({})),
						base64.b64encode(cPickle.dumps({})),
						base64.b64encode(cPickle.dumps({})),
						base64.b64encode(cPickle.dumps(self.result['inventory'][ITEM_TYPE_INDICES['tankman']])),
						base64.b64encode(cPickle.dumps({})),
						base64.b64encode(cPickle.dumps({})),
						base64.b64encode(cPickle.dumps({}))))
			except Exception as e:
				raise Exception("GetInventoryData :: Error occurred while writing inventory data (init)=%s" % e)
		else:
			for k, v in i_result.items():
				self.result['inventory'].update({int(k): cPickle.loads(base64.b64decode(v))})  # dict
				# self.result['inventory'][ITEM_TYPE_INDICES[k]] = self.result['inventory'].pop(str(k))
		c.close()
		connection.commit()
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		if DO_DEBUG: TRACE_MSG('[DatabaseHandler] GetInventoryData (foreground) :: databaseID=%s' % self.normalizedName)
		self.callback(self.result)


class SetInventoryData(BackgroundTask.BackgroundTask):
	"""
	Updates the inventory data in the database.
	Data keys must match order of columns.
	"""
	
	def __init__(self, normalizedName, data, callback, columns):
		self.normalizedName = normalizedName
		self.columns = columns
		self.data = data
		self.callback = callback
		self.result = {}
	
	def doBackgroundTask(self, bgTaskMgr, connection):
		if DO_DEBUG: TRACE_MSG(
			'[DatabaseHandler] SetInventoryData (background) :: normalizedName=%s' % self.normalizedName)
		if not self.columns: raise Exception("SetInventoryData :: No columns specified")
		if self.data['inventory']: self.data = self.data.pop('inventory')
		c = connection.cursor(dictionary=True)
		for col in self.columns:
			c.execute("UPDATE inventory SET `{}`=%s WHERE email=%s".format(str(col)),
			          (base64.b64encode(cPickle.dumps(self.data[col])), self.normalizedName))
		c.close()
		connection.commit()
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		if DO_DEBUG: TRACE_MSG(
			'[DatabaseHandler] SetInventoryData (foreground) :: normalizedName=%s' % self.normalizedName)
		self.callback(self.result)


class GetStatsData(BackgroundTask.BackgroundTask):
	"""
	Queries player database for stats data.
	"""
	
	def __init__(self, normalizedName, callback, columns):
		self.normalizedName = normalizedName
		self.columns = columns
		self.callback = callback
		self.result = {}
	
	def doBackgroundTask(self, bgTaskMgr, connection):
		if DO_DEBUG: TRACE_MSG('[DatabaseHandler] GetStatsData (background) :: normalizedName=%s' % self.normalizedName)
		if not self.columns: raise Exception("GetStatsData :: No columns specified")
		if self.columns != '*' and type(self.columns) == list and len(self.columns) > 0:
			self.columns = ', '.join(self.columns)
		c = connection.cursor(dictionary=True)
		c.execute("""SELECT {} FROM stats WHERE email=%s""".format(self.columns), (self.normalizedName,))
		s_result = c.fetchone()
		if s_result is None:
			self.result.update(initEmptyStats())  # dict
			try:
				c.execute(
					"""INSERT INTO stats (email, account, cache, economics, offers, stats, intUserSettings, eventsData) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
					(
						self.normalizedName,
						base64.b64encode(cPickle.dumps(self.result['account'])),
						base64.b64encode(cPickle.dumps(self.result['cache'])),
						base64.b64encode(cPickle.dumps(self.result['economics'])),
						base64.b64encode(cPickle.dumps(self.result['offers'])),
						base64.b64encode(cPickle.dumps(self.result['stats'])),
						base64.b64encode(cPickle.dumps(self.result[('intUserSettings', '_r')])),
						base64.b64encode(cPickle.dumps(self.result[('eventsData', '_r')]))))
			except Exception as e:
				raise Exception("GetStatsData :: Error occurred while writing stats data (init)=%s" % e)
			self.result[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS] = zlib.compress(
				cPickle.dumps(self.result[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS]))
		else:  # all of this shit is hacky
			for k, v in s_result.items():
				if k == 'intUserSettings': k = ('intUserSettings', '_r')
				if k == 'eventsData': k = ('eventsData', '_r')
				self.result.update({k: cPickle.loads(base64.b64decode(v))})  # dict
			if self.result.get("('intUserSettings', '_r')", False): self.result[
				('intUserSettings', '_r')] = self.result.pop("('intUserSettings', '_r')")
			if self.result.get("('eventsData', '_r')", False): self.result[('eventsData', '_r')] = self.result.pop(
				"('eventsData', '_r')")
			# self.result[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS] = zlib.compress(cPickle.dumps(self.result[('eventsData', '_r')][EVENT_CLIENT_DATA.NOTIFICATIONS]))
			
			if self.result.get('account', False):
				if DO_DEBUG: INFO_MSG('[DatabaseHandler] GetStatsData premiumcheck :: top')
				current_time = int(time.time())
				attrs = self.result['account']['attrs']  # checks only
				premium_epoch = self.result['account']['premiumExpiryTime']  # checks only
				
				if (not attrs & ACCOUNT_ATTR.PREMIUM) and premium_epoch > current_time:
					self.result['account']['attrs'] |= ACCOUNT_ATTR.PREMIUM
				if attrs & ACCOUNT_ATTR.PREMIUM and premium_epoch < current_time:
					self.result['account']['attrs'] &= ~ACCOUNT_ATTR.PREMIUM
					self.result['account']['premiumExpiryTime'] = 0
				if DO_DEBUG: INFO_MSG('[DatabaseHandler] GetStatsData premiumcheck :: bottom')
		c.close()
		connection.commit()
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		if DO_DEBUG: TRACE_MSG('[DatabaseHandler] GetStatsData (foreground) :: normalizedName=%s' % self.normalizedName)
		self.callback(self.result)


class SetStatsData(BackgroundTask.BackgroundTask):
	"""
	Updates stats data in player database.
	"""
	
	def __init__(self, normalizedName, data, callback, columns):
		self.normalizedName = normalizedName
		self.columns = columns
		self.data = data
		self.callback = callback
		self.result = False
	
	def doBackgroundTask(self, bgTaskMgr, connection):
		if DO_DEBUG: TRACE_MSG('[DatabaseHandler] SetStatsData (background) :: normalizedName=%s' % self.normalizedName)
		if not self.columns: raise Exception("SetStatsData :: No columns specified")
		if ('intUserSettings', '_r') in self.data: self.data['intUserSettings'] = self.data.pop(
			('intUserSettings', '_r'))
		if ('eventsData', '_r') in self.data: self.data['eventsData'] = self.data.pop(('eventsData', '_r'))
		c = connection.cursor(dictionary=True)
		for col in self.columns:
			c.execute("UPDATE stats SET {}=%s WHERE email=%s".format(col),
			          (base64.b64encode(cPickle.dumps(self.data[col])), self.normalizedName))
		c.close()
		connection.commit()
		
		self.result = True
		
		bgTaskMgr.addMainThreadTask(self)
	
	def doMainThreadTask(self, bgTaskMgr):
		if DO_DEBUG: TRACE_MSG('[DatabaseHandler] SetStatsData (foreground) :: normalizedName=%s' % self.normalizedName)
		self.callback(self.result)


class GetDossierData(BackgroundTask.BackgroundTask):
	"""
	Queries player database for stats data.
	"""
	
	def __init__(self, databaseID, callback):
		self.databaseID = databaseID
		self.callback = callback
		self.result = {}
		self.filepath = None
	
	def doBackgroundTask(self, bgTaskMgr, threadData):
		if DO_DEBUG: TRACE_MSG('[DatabaseHandler] GetDossierData (background) :: databaseID=%s' % self.databaseID)
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
