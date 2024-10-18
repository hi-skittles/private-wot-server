import cPickle
import zlib

from Requests import AccountUpdates
from adisp import async, process
from bwdebug import DEBUG_MSG, TRACE_MSG
import items
from db_scripts.responders import SyncDataHandler, StatsHandler, ShopHandler, DossierHandler
from collections import namedtuple

from DatabaseWorker import Helper

import BigWorld
import AccountCommands


# RequestResult = namedtuple('RequestResult', ['resultID', 'errorStr', 'data'])

BASE_REQUESTS = {}
shopItems = {}
Helper = Helper()

items.init(True, shopItems)

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


# notes:
# tank = vehicles.getVehicleType(3089)
# print tank.autounlockedItems


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
def exchangeFreeXP(proxy, requestID, *args):
    array, int2 = args[0]
    DEBUG_MSG('AccountCommands.CMD_BUY_AND_EQUIP_ITEM :: ', array, int2)
    proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, '')

@baseRequest(AccountCommands.CMD_EXCHANGE)
@process
def exchangeCredits(proxy, requestID, int1, int2, int3):
    DEBUG_MSG('AccountCommands.CMD_EXCHANGE :: credits=%s' % int2)
    credits = int2
    rdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.databaseID)
    result, msg, udata = AccountUpdates.__exchangeGold(credits, rdata)
    if result > 0:
        DEBUG_MSG('AccountCommands.CMD_EXCHANGE :: success=%s' % result)
        udata.update({'rev': 1, 'prevRev': 0})
        proxy.client.update(cPickle.dumps(udata))
        proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')
        udata.pop('rev')
        udata.pop('prevRev')
        yield async(StatsHandler.update_stats, cbname='callback')(proxy.databaseID, udata)
    else:
        DEBUG_MSG('AccountCommands.CMD_EXCHANGE :: failure=%s' % result)
        proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, 'Not enough gold')

@baseRequest(AccountCommands.CMD_PREMIUM)
@process
def premium(proxy, requestID, int1, int2, int3):
    DEBUG_MSG('AccountCommands.CMD_PREMIUM :: days=%s' % int2)
    shopRev = int1
    extend_by_days = int2
    rdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.databaseID)
    TRACE_MSG('MAXIMUS %s ' % rdata[('eventsData', '_r')])
    result, msg, udata = AccountUpdates.__addPremiumTime(extend_by_days, rdata)
    if result > 0:
        DEBUG_MSG('AccountCommands.CMD_PREMIUM :: success=%s' % result)
        udata.update({'rev': 1, 'prevRev': 0})
        proxy.client.update(cPickle.dumps(udata))
        proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')
        udata.pop('rev')
        udata.pop('prevRev')
        yield async(StatsHandler.update_stats, cbname='callback')(proxy.databaseID, udata)
    else:
        DEBUG_MSG('AccountCommands.CMD_PREMIUM :: failure=%s' % result)
        proxy.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, 'Not enough gold')

@baseRequest(AccountCommands.CMD_ADD_INT_USER_SETTINGS)
@process    # ugly i know, but it doesn't WORK the other way around sooo
def addIntUserSettings(proxy, requestID, settings):
    DEBUG_MSG('AccountCommands.CMD_ADD_INT_USER_SETTINGS :: ', settings)
    
    # this stores the result of the callback into rdata variable instead of having to write a callback function above
    # any variables normally passed into the async method instead get passed as such, minus the actual callback arg: foo(arg1, arg2, callback) -> data = yield async(foo)(arg1, arg2)
    rdata = yield async(StatsHandler.get_stats, cbname='callback')(proxy.databaseID)
    
    # processing settings
    bdata = {'rev': requestID, 'prevRev': 0, 'intUserSettings': {}}
    for i in range(0, len(settings), 2):
        k, v = int(settings[i]), int(settings[i + 1])
        rdata[('intUserSettings', '_r')][k] = v
        bdata['intUserSettings'][k] = v
    # send new settings to client
    proxy.client.update(cPickle.dumps(bdata))
    # send new settings to db
    # named "nothing" here because this method will return True if successful
    nothing = yield async(StatsHandler.update_stats, cbname='callback')(proxy.databaseID, rdata)
    
    proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')

@baseRequest(AccountCommands.CMD_REQ_SERVER_STATS)
def serverStats(proxy, requestID, int1, int2, int3):
    data = {
        'clusterCCU': len(BigWorld.entities.keys()),
        'regionCCU': len(BigWorld.entities.keys())
    }
    proxy.client.receiveServerStats(data)
    proxy.client.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')

@baseRequest(AccountCommands.CMD_COMPLETE_TUTORIAL)
def completeTutorial(proxy, requestID, revision, dataLen, dataCrc):
    DEBUG_MSG('AccountCommands.CMD_COMPLETE_TUTORIAL :: ', revision, dataLen, dataCrc)
    proxy.client.onCmdResponseExt(requestID, AccountCommands.RES_SUCCESS, '', {})

# inventory[inventory, cache], stats[stats, account, economics, cache], questProgress[quests, tokens, potapovQuests], trader[offers], intUserSettings[(see comment below for more info)], clubs[cache[relatedToClubs, cybersportSeasonInProgress]]
@baseRequest(AccountCommands.CMD_SYNC_DATA)
@process
def syncData(proxy, requestID, revision, crc, _):
    DEBUG_MSG('AccountCommands.CMD_SYNC_DATA :: ', revision, crc)
    # the client normally does not request a fullsync. nyi on requesting a partial sync or whatever who cares but since its not requesting a full sync i will return the partial key instead of full sync key
    # intUserSettings if updating only partial setting. the weird tuple, ('intUserSettings', '_r'), as primary key if its a full sync
    
    data = {'rev': revision + 1, 'prevRev': revision}
    rdata = yield async(SyncDataHandler.get_sync_data, cbname='callback')(proxy.databaseID)
    data.update(rdata)
    proxy.client.onCmdResponseExt(requestID, AccountCommands.RES_SUCCESS, '', cPickle.dumps(data))

@baseRequest(AccountCommands.CMD_SYNC_SHOP)
def syncShop(proxy, requestID, revision, dataLen, dataCrc):
    DEBUG_MSG('AccountCommands.CMD_SYNC_SHOP :: ', revision, dataLen, dataCrc)
    # if there is a desync then we can use AccountCommands.RES_SHOP_DESYNC as our result ID, which requires adding shopRev; else not
    shop = ShopHandler.get_shop()
    shop.update({'prevRev': revision, 'rev': 2})
    # foo = zlib.compress(cPickle.dumps(shop))
    #
    # if shop['rev'] == revision:
    #     DEBUG_MSG('AccountCommands.CMD_SYNC_SHOP :: revisions match, telling client to use its cache')
    #     proxy.client.onCmdResponse(requestID, AccountCommands.RES_CACHE, '')
    # elif shop['rev'] != revision and dataLen == len(foo) and dataCrc == zlib.crc32(foo):
    #     DEBUG_MSG('AccountCommands.CMD_SYNC_SHOP :: revisions do not match, but other shit matches so oh well use cache')
    #     # packStream(proxy, requestID, shop)
    #     proxy.client.onCmdResponseExt(requestID, AccountCommands.RES_CACHE, '', cPickle.dumps({'shopRev': 1}))
    # elif revision == 0:
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
    _GUI_CTX = cPickle.dumps({
        'databaseID': proxy.databaseID,
        'logUXEvents': True,
        'aogasStartedAt': None,
        'sessionStartedAt': 0,
        'isAogasEnabled': False,
        'collectUiStats': False,
        'isLongDisconnectedFromCenter': False,
    })
    proxy.client.showGUI(_GUI_CTX)

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

