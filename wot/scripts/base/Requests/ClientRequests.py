import cPickle, time, zlib

from Requests import AccountUpdates
from adisp import async, process
from bwdebug import DEBUG_MSG, ERROR_MSG, TRACE_MSG
from db_scripts.responders import QuestsHandler, InventoryHandler, StatsHandler, ShopHandler, DossierHandler
from collections import namedtuple
from items import ITEM_TYPE_INDICES

import BigWorld
import AccountCommands
from enumerations import Enumeration

SM_TYPE = Enumeration(
	'System message type',
	['Error',
	 'Warning',
	 'Information',
	 'GameGreeting',
	 'PowerLevel',
	 'FinancialTransactionWithGold',
	 'FinancialTransactionWithCredits',
	 'FortificationStartUp',
	 'PurchaseForGold',
	 'DismantlingForGold',
	 'PurchaseForCredits',
	 'Selling',
	 'Remove',
	 'Repair',
	 'CustomizationForGold',
	 'CustomizationForCredits'])
BASE_REQUESTS = {}


# RequestResult = namedtuple('RequestResult', ['resultID', 'errorStr', 'data'])
def baseRequest(cmdID):
	def wrapper(func):
		def requester(proxy, requestID, *args):
			result = func(proxy, requestID, *args)
		
		# return proxy, requestID, result.resultID, result.errorStr, result.data
		BASE_REQUESTS[cmdID] = requester
		return func
	
	return wrapper


def packStream(proxy, requestID, data):
	data = zlib.compress(cPickle.dumps(data))
	desc = cPickle.dumps((len(data), zlib.crc32(data)))
	return proxy.streamStringToClient(data, desc, requestID)


@baseRequest(AccountCommands.CMD_REQ_PREBATTLES)
def reqPrebattles(proxy, requestID, args):
	DEBUG_MSG('AccountCommands.CMD_REQ_PREBATTLES :: ', args)
	proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, 'Deprecated')


@baseRequest(AccountCommands.CMD_ENQUEUE_TUTORIAL)
def enqueueTutorial(proxy, requestID, int1, int2, int3):
	DEBUG_MSG('AccountCommands.CMD_ENQUEUE_TUTORIAL :: ', int1, int2, int3)
	proxy.onTutorialEnqueued('string', int1)
	proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, 'Deprecated')


@baseRequest(AccountCommands.CMD_BUY_VEHICLE)
@process
def buyVehicle(proxy, requestID, args):
	if len(args) != 5:
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_WRONG_ARGS, 'Invalid arguments')
		return
	
	shopRev, vehTypeCompDescr, flags, crew_level, int3 = args
	DEBUG_MSG('AccountCommands.CMD_BUY_VEHICLE :: ', shopRev, vehTypeCompDescr, flags, crew_level, int3)
	s_data = yield async(StatsHandler.get_stats, cbname='callback')(proxy.normalizedName, ['stats', 'economics'])
	i_data = yield async(InventoryHandler.get_inventory, cbname='callback')(proxy.normalizedName, ['vehicle', 'tankman'])
	result, msg, s_data, i_data = AccountUpdates.__buyVehicle(s_data, i_data, shopRev, vehTypeCompDescr, flags,
	                                                          crew_level, int3)
	
	# this is the only thing the client needs in .update ...
	cdata = {'rev': requestID, 'prevRev': requestID - 1,
	         'inventory': {
		         1: {'compDescr': None, 'crew': None, 'eqs': None, 'eqsLayout': None, 'settings': None,
		             'shellsLayout': None},
		         8: {'compDescr': None, 'vehicle': None}
	         },
	         'stats': {
		         'gold': None, 'maxResearchedLevelByNation': None, 'vehTypeXP': None, 'unlocks': None, 'credits': None
	         }
	         }
	
	if result > 0:
		DEBUG_MSG('AccountCommands.CMD_BUY_VEHICLE :: success=%s' % result)
		
		cdata['inventory'][ITEM_TYPE_INDICES['vehicle']]['compDescr'] = \
			i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['compDescr']
		cdata['inventory'][ITEM_TYPE_INDICES['vehicle']]['crew'] = i_data['inventory'][ITEM_TYPE_INDICES['vehicle']][
			'crew']
		cdata['inventory'][ITEM_TYPE_INDICES['vehicle']]['eqs'] = i_data['inventory'][ITEM_TYPE_INDICES['vehicle']][
			'eqs']
		cdata['inventory'][ITEM_TYPE_INDICES['vehicle']]['eqsLayout'] = \
			i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['eqsLayout']
		cdata['inventory'][ITEM_TYPE_INDICES['vehicle']]['settings'] = \
			i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['settings']
		cdata['inventory'][ITEM_TYPE_INDICES['vehicle']]['shellsLayout'] = \
			i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['shellsLayout']
		
		cdata['inventory'][ITEM_TYPE_INDICES['tankman']]['compDescr'] = \
			i_data['inventory'][ITEM_TYPE_INDICES['tankman']]['compDescr']
		cdata['inventory'][ITEM_TYPE_INDICES['tankman']]['vehicle'] = i_data['inventory'][ITEM_TYPE_INDICES['tankman']][
			'vehicle']
		
		cdata['stats']['gold'] = s_data['stats']['gold']
		cdata['stats']['credits'] = s_data['stats']['credits']
		cdata['stats']['maxResearchedLevelByNation'] = s_data['stats']['maxResearchedLevelByNation']
		cdata['stats']['vehTypeXP'] = s_data['stats']['vehTypeXP']
		cdata['stats']['unlocks'] = s_data['stats']['unlocks']
		
		is_invalid_data, invalid_data = False, None
		# ensure no value in cdata is None before sending to client
		for k, v in cdata.iteritems():
			if v is None:
				is_invalid_data, invalid_data = True, k
		
		if not is_invalid_data:
			proxy.client.update(cPickle.dumps(cdata))
			proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')
			# ...whereas we still store the full dict to db
			proxy.writeToDB()
			yield async(StatsHandler.update_stats, cbname='callback')(proxy.normalizedName, s_data, ['stats', 'economics'])
			yield async(InventoryHandler.set_inventory, cbname='callback')(proxy.normalizedName, i_data,
			                                                               ['vehicle', 'tankman'])
		else:
			ERROR_MSG('AccountCommands.CMD_BUY_VEHICLE :: None value in cdata=%s' % invalid_data)
			proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, 'None value in cdata')
	else:
		DEBUG_MSG('AccountCommands.CMD_BUY_VEHICLE :: failure=', result, msg)
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_WRONG_ARGS, msg)


@baseRequest(AccountCommands.CMD_BUY_SLOT)
@process
def buySlot(proxy, requestID, int1, _, __):
	DEBUG_MSG('AccountCommands.CMD_BUY_SLOT :: ', int1)
	shopRev = int1
	rdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.normalizedName, 'stats')
	result, msg, udata = AccountUpdates.__buySlot(rdata)
	
	# this is the only thing the client needs in .update ...
	cdata = {'rev': requestID, 'prevRev': requestID - 1, 'stats': {'slots': None, 'gold': None}}
	
	if result > 0:
		DEBUG_MSG('AccountCommands.CMD_BUY_SLOT :: success=%s' % result)
		cdata['stats']['slots'] = udata['stats']['slots']
		cdata['stats']['gold'] = udata['stats']['gold']
		proxy.client.update(cPickle.dumps(cdata))
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')
		# ...whereas we still store the full dict to db
		proxy.writeToDB()
		yield async(StatsHandler.update_stats, cbname='callback')(proxy.normalizedName, udata, ['stats'])
	else:
		DEBUG_MSG('AccountCommands.CMD_BUY_SLOT :: failure=%s' % result)
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, msg)


@baseRequest(AccountCommands.CMD_VEH_CAMOUFLAGE)
@process
def vehicleCamouflage(proxy, requestID, *args):
	int1, int2, int3, int4, int5 = args[0]
	DEBUG_MSG('AccountCommands.CMD_VEH_CAMOUFLAGE :: ', int1, int2, int3, int4, int5)
	proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, '')


@baseRequest(AccountCommands.CMD_BUY_AND_EQUIP_ITEM)
@process
def buyAndEquipItem(proxy, requestID, *args):
	int1, int2, int3, int4, int5, int6 = args[0]
	DEBUG_MSG('AccountCommands.CMD_BUY_AND_EQUIP_ITEM :: ', int1, int2, int3, int4, int5, int6)
	proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, '')


@baseRequest(AccountCommands.CMD_FREE_XP_CONV)
@process
def exchangeFreeXP(proxy, requestID, args):
	DEBUG_MSG('AccountCommands.CMD_FREE_XP_CONV')
	wantedXP = args[1]
	vehTypeDescrs = args[2:]
	rdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.normalizedName, 'stats')
	result, msg, udata = AccountUpdates.__exchangeFreeXP(wantedXP, rdata, vehTypeDescrs)
	
	cdata = {'rev': requestID, 'prevRev': requestID - 1, 'stats': {'gold': None, 'freeXP': None, 'vehTypeXP': None}}
	
	if result > 0:
		DEBUG_MSG('AccountCommands.CMD_FREE_XP_CONV :: success=%s' % result)
		
		cdata['stats']['gold'] = udata['stats']['gold']
		cdata['stats']['freeXP'] = udata['stats']['freeXP']
		cdata['stats']['vehTypeXP'] = udata['stats']['vehTypeXP']
		
		proxy.client.update(cPickle.dumps(cdata))
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')
		proxy.writeToDB()
		yield async(StatsHandler.update_stats, cbname='callback')(proxy.normalizedName, udata, ['stats'])
	else:
		DEBUG_MSG('AccountCommands.CMD_FREE_XP_CONV :: failure=%s' % result)
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, msg)


@baseRequest(AccountCommands.CMD_UNLOCK)
@process
def unlockItem(proxy, requestID, vehTypeCompDescr, unlockIdx, int1):
	DEBUG_MSG('AccountCommands.CMD_UNLOCK :: ', vehTypeCompDescr, unlockIdx, int1)
	rdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.normalizedName, ['stats', 'economics'])
	oldEliteVehicles = rdata['stats']['eliteVehicles']
	result, msg, udata = AccountUpdates.__unlockItem(vehTypeCompDescr, unlockIdx, rdata)
	
	# this is the only thing the client needs in .update ...
	cdata = {'rev': requestID, 'prevRev': requestID - 1,
	         'stats': {'vehTypeXP': None, 'freeXP': None, 'unlocks': None, 'eliteVehicles': None},
	         'economics': {'eliteVehicles': None}
	         }
	
	if result > 0:
		DEBUG_MSG('AccountCommands.CMD_UNLOCK :: success=%s' % result)
		cdata['stats']['vehTypeXP'] = udata['stats']['vehTypeXP']
		cdata['stats']['freeXP'] = udata['stats']['freeXP']
		cdata['stats']['unlocks'] = udata['stats']['unlocks']
		cdata['economics']['eliteVehicles'] = udata['economics']['eliteVehicles']
		
		if oldEliteVehicles != udata['stats']['eliteVehicles']:
			cdata['stats']['eliteVehicles'] = udata['stats']['eliteVehicles']
		else:
			print cdata['stats'].pop('eliteVehicles')
		
		proxy.client.update(cPickle.dumps(cdata))
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')
		
		# ...whereas we still store the full dict to db
		proxy.writeToDB()
		yield async(StatsHandler.update_stats, cbname='callback')(proxy.normalizedName, udata, ['stats', 'economics'])
	else:
		DEBUG_MSG('AccountCommands.CMD_UNLOCK :: failure=%s' % result)
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, msg)


@baseRequest(AccountCommands.CMD_EXCHANGE)
@process
def exchangeCredits(proxy, requestID, int1, int2, int3):
	DEBUG_MSG('AccountCommands.CMD_EXCHANGE :: credits=%s' % int2)
	credits = int2
	rdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.normalizedName, 'stats')
	result, msg, udata = AccountUpdates.__exchangeGold(credits, rdata)
	
	# this is the only thing the client needs in .update ...
	cdata = {'rev': requestID, 'prevRev': requestID - 1, 'stats': {'gold': None, 'credits': None}}
	
	if result > 0:
		DEBUG_MSG('AccountCommands.CMD_EXCHANGE :: success=%s' % result)
		#   should i ensure these are not None before being sent to client?
		cdata['stats']['gold'] = udata['stats']['gold']
		cdata['stats']['credits'] = udata['stats']['credits']
		
		proxy.client.update(cPickle.dumps(cdata))
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')
		# ...whereas we still store the full dict to db
		proxy.writeToDB()
		yield async(StatsHandler.update_stats, cbname='callback')(proxy.normalizedName, udata, ['stats'])
	else:
		DEBUG_MSG('AccountCommands.CMD_EXCHANGE :: failure=%s' % result)
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, msg)


@baseRequest(AccountCommands.CMD_PREMIUM)
@process
def premium(proxy, requestID, int1, int2, int3):
	DEBUG_MSG('AccountCommands.CMD_PREMIUM :: days=%s' % int2)
	shopRev = int1
	extend_by_days = int2
	rdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.normalizedName, ['account', 'stats'])
	TRACE_MSG('[premium]', rdata)
	result, msg, udata = AccountUpdates.__addPremiumTime(extend_by_days, rdata)
	
	# this is the only thing the client needs in .update ...
	cdata = {'rev': requestID, 'prevRev': requestID - 1, 'stats': {'gold': None},
	         'account': {'premiumExpiryTime': None, 'attrs': None}}
	
	if result > 0:
		DEBUG_MSG('AccountCommands.CMD_PREMIUM :: success=%s' % result)
		cdata['stats']['gold'] = udata['stats']['gold']
		cdata['account']['premiumExpiryTime'] = udata['account']['premiumExpiryTime']
		cdata['account']['attrs'] = udata['account']['attrs']
		
		proxy.client.update(cPickle.dumps(cdata))
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')
		# ...whereas we still store the full dict to db
		proxy.writeToDB()
		yield async(StatsHandler.update_stats, cbname='callback')(proxy.normalizedName, udata, ['account', 'stats'])
	else:
		DEBUG_MSG('AccountCommands.CMD_PREMIUM :: failure=%s' % result)
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, msg)


@baseRequest(AccountCommands.CMD_ADD_INT_USER_SETTINGS)
@process  # ugly i know, but it doesn't WORK the other way around sooo
def addIntUserSettings(proxy, requestID, settings):
	DEBUG_MSG('AccountCommands.CMD_ADD_INT_USER_SETTINGS :: ', settings)
	
	# this stores the result of the callback into rdata variable instead of having to write a callback function above
	# any variables normally passed into the async method instead get passed as such, minus the actual callback arg: foo(arg1, arg2, callback) -> data = yield async(foo)(arg1, arg2)
	rdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.normalizedName, 'intUserSettings')
	
	# processing settings
	cdata = {'rev': requestID, 'prevRev': requestID - 1, 'intUserSettings': {}}
	for i in range(0, len(settings), 2):
		k, v = int(settings[i]), int(settings[i + 1])
		rdata[('intUserSettings', '_r')][k] = v
		cdata['intUserSettings'][k] = v
	
	# send new settings to db
	# named "nothing" here because this method will return True if successful
	n = yield async(StatsHandler.update_stats, cbname='callback')(proxy.normalizedName, rdata, ['intUserSettings'])
	
	# send new settings to client
	proxy.client.update(cPickle.dumps(cdata))
	if n:
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')
		proxy.writeToDB()
	else:
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, 'Server error')


@baseRequest(AccountCommands.CMD_REQ_SERVER_STATS)
def serverStats(proxy, requestID, int1, int2, int3):
	data = {
		'clusterCCU': len([entity for entity in BigWorld.entities.values() if entity.className == 'Account']),
		'regionCCU': len([entity for entity in BigWorld.entities.values() if entity.className == 'Account'])
	}
	proxy.client.receiveServerStats(data)
	proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')


@baseRequest(AccountCommands.CMD_COMPLETE_TUTORIAL)
def completeTutorial(proxy, requestID, revision, dataLen, dataCrc):
	DEBUG_MSG('AccountCommands.CMD_COMPLETE_TUTORIAL :: ', revision, dataLen, dataCrc)
	proxy.client.onCmdResponseExt(requestID, AccountCommands.RES_FAILURE, '', {})


# inventory[inventory, cache], stats[stats, account, economics, cache], questProgress[quests, tokens, potapovQuests], trader[offers], intUserSettings[(see comment below for more info)], clubs[cache[relatedToClubs, cybersportSeasonInProgress]]
@baseRequest(AccountCommands.CMD_SYNC_DATA)
@process
def syncData(proxy, requestID, revision, crc, _):
	DEBUG_MSG('AccountCommands.CMD_SYNC_DATA :: ', revision, crc)
	# the client normally does not request a fullsync. nyi on requesting a partial sync or whatever who cares but since its not requesting a full sync i will return the partial key instead of full sync key
	# intUserSettings if updating only partial setting. the weird tuple, ('intUserSettings', '_r'), as primary key if its a full sync
	
	data = {'rev': revision + 1, 'prevRev': revision}
	qrdata = yield async(QuestsHandler.get_quests, cbname='callback')(proxy.normalizedName,
	                                                                  ['tokens', 'potapovQuests', 'quests'])
	irdata = yield async(InventoryHandler.get_inventory, cbname='callback')(proxy.normalizedName,
	                                                                        ['vehicle', 'vehicleChassis',
	                                                                         'vehicleTurret', 'vehicleGun',
	                                                                         'vehicleEngine', 'vehicleFuelTank',
	                                                                         'vehicleRadio', 'tankman',
	                                                                         'optionalDevice', 'shell', 'equipment'])
	srdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.normalizedName,
	                                                                ['account', 'cache', 'economics', 'offers', 'stats',
	                                                                 'intUserSettings', 'eventsData'])
	data.update(qrdata)
	data.update(irdata)
	data.update(srdata)
	
	# show gui to client
	_GUI_CTX = cPickle.dumps({
		'databaseID': proxy.databaseID,
		'logUXEvents': True,
		'aogasStartedAt': time.time(),
		'sessionStartedAt': time.time(),
		'isAogasEnabled': True,
		'collectUiStats': False,
		'isLongDisconnectedFromCenter': False,
	})
	proxy.client.showGUI(_GUI_CTX)
	proxy.client.pushClientMessage("Thank you for downloading WoT Offline 9.7", SM_TYPE.FortificationStartUp)
	proxy.client.onCmdResponseExt(requestID, AccountCommands.RES_SUCCESS, '', cPickle.dumps(data))


@baseRequest(AccountCommands.CMD_SYNC_SHOP)
def syncShop(proxy, requestID, revision, dataLen, dataCrc):
	DEBUG_MSG('AccountCommands.CMD_SYNC_SHOP :: ', revision, dataLen, dataCrc)
	# if there is a desync then we can use AccountCommands.RES_SHOP_DESYNC as our result ID, which requires adding shopRev; else not
	shop = ShopHandler.get_shop()
	shop.update({'prevRev': revision})
	foo = zlib.compress(cPickle.dumps(shop))
	
	# if shop['rev'] == revision:
	#     DEBUG_MSG('AccountCommands.CMD_SYNC_SHOP :: revisions match, telling client to use its cache')
	#     proxy.client.onCmdResponse(requestID, AccountCommands.RES_CACHE, '')
	if dataLen == len(foo) and dataCrc == zlib.crc32(foo):
		DEBUG_MSG(
			'AccountCommands.CMD_SYNC_SHOP :: revisions do not match, but other shit matches so oh well use cache')
		proxy.client.onCmdResponseExt(requestID, AccountCommands.RES_CACHE, '', cPickle.dumps({'shopRev': 2}))
	else:
		DEBUG_MSG('AccountCommands.CMD_SYNC_SHOP :: client requested full sync, sending full shop data to client')
		packStream(proxy, requestID, shop)
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_STREAM, '')


@baseRequest(AccountCommands.CMD_SYNC_DOSSIERS)
def syncDossiers(proxy, requestID, version, maxChangeTime, _):
	DEBUG_MSG('AccountCommands.CMD_SYNC_DOSSIERS :: ', version, maxChangeTime)
	
	def callback(data):
		packStream(proxy, requestID, (version + 1, data))
		proxy.client.onCmdResponse(requestID, AccountCommands.RES_STREAM, '')
	
	DossierHandler.get_dossiers(proxy.databaseID, callback)


@baseRequest(-32767)
def sendGUI(proxy, requestID, _):
	# _GUI_CTX = cPickle.dumps({
	# 	'databaseID': proxy.databaseID,
	# 	'logUXEvents': True,
	# 	'aogasStartedAt': time.time(),
	# 	'sessionStartedAt': time.time(),
	# 	'isAogasEnabled': True,
	# 	'collectUiStats': False,
	# 	'isLongDisconnectedFromCenter': False,
	# })
	# proxy.client.showGUI(_GUI_CTX)
	# proxy.client.pushClientMessage("Thank you for downloading WoT Offline 9.7", SM_TYPE.FortificationStartUp)
	proxy.client.onCmdResponse(requestID, AccountCommands.RES_NON_PLAYER, 'Deprecated')


def sendPushNotifToClient(proxy, no_type, message):
	proxy.client.pushClientMessage(message, no_type)


@baseRequest(AccountCommands.CMD_SET_LANGUAGE)
def setLanguage(proxy, requestID, language):
	DEBUG_MSG('AccountCommands.CMD_SET_LANGUAGE :: ', language)
	packStream(proxy, requestID, language)
	proxy.client.onCmdResponse(requestID, AccountCommands.RES_STREAM, '')


@baseRequest(AccountCommands.CMD_VERIFY_FIN_PSWD)
def verifyFinPswd(proxy, requestID, password):
	DEBUG_MSG('AccountCommands.CMD_VERIFY_FIN_PSWD :: ', password)
	proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, 'Invalid or NYI')


@baseRequest(AccountCommands.CMD_REQ_PLAYER_INFO)
def reqPlayerInfo(proxy, requestID, databaseID):
	DEBUG_MSG('AccountCommands.CMD_REQ_PLAYER_INFO :: ', databaseID)
	pass


@baseRequest(AccountCommands.CMD_REQ_VEHICLE_DOSSIER)
def reqVehicleDossier(proxy, databaseID, vehTypeCompDescr):
	DEBUG_MSG('AccountCommands.CMD_REQ_VEHICLE_DOSSIER :: ', vehTypeCompDescr)


@baseRequest(AccountCommands.CMD_REQ_ACCOUNT_DOSSIER)
def reqAccountDossier(proxy, requestID, databaseID):
	DEBUG_MSG('AccountCommands.CMD_REQ_ACCOUNT_DOSSIER :: databaseID=%s' % databaseID)
	pass


def getAccountInfoFromDBID():
	pass
	return


def getDossierFromDBID():
	pass
	return
