from random import randint

import BigWorld
from BigWorld import Proxy
from collections import deque

import AccountCommands
from Requests.AccountRequests import BASE_REQUESTS
from adisp import async, process
from bwdebug import DEBUG_MSG, TRACE_MSG, ERROR_MSG, INFO_MSG
from db_scripts.handlers import StatsHandler


def onComplete(entity):
	if entity is not None:
		DEBUG_MSG('onComplete', entity)
	else:
		ERROR_MSG('onComplete :: entity is None')


class Account(BigWorld.Proxy):
	def __init__(self):
		BigWorld.Proxy.__init__(self)
		self.serverSettings = {
			'isGoldFishEnabled': False,
			'isVehicleRestoreEnabled': False,
			'isFalloutQuestEnabled': False,
			'isClubsEnabled': False,
			'isSandboxEnabled': False,
			'isFortBattleDivisionsEnabled': False,
			'isFortsEnabled': False,
			'isEncyclopediaEnabled': False,  # 'token'
			'isStrongholdsEnabled': False,
			'isRegularQuestEnabled': False,
			'isSpecBattleMgrEnabled': False,
			'isTankmanRestoreEnabled': False,
			'isPotapovQuestEnabled': False,
			'reCaptchaParser': '',
			
			'forbiddenSortiePeripheryIDs': (),
			'newbieBattlesCount': 5,
			
			'randomMapsForDemonstrator': {},
			
			'forbidSPGinSquads': False,
			'forbiddenRatedBattles': {},
			'forbiddenSortieHours': (14,),
			'forbiddenFortDefenseHours': (0, 1, 2, 3, 4),
			
			'eSportSeasonID': 1,
			'eSportSeasonStart': 1442318400,
			'eSportSeasonFinish': 1472688000,
			
			'regional_settings': {'starting_day_of_a_new_week': 0, 'starting_time_of_a_new_game_day': 0,
			                      'starting_time_of_a_new_day': 0, 'starting_day_of_a_new_weak': 0},
			
			'xmpp_enabled': False,
			'xmpp_port': 0,
			'xmpp_host': '',
			'xmpp_muc_enabled': False,
			'xmpp_muc_services': [],
			'xmpp_resource': '',
			'xmpp_bosh_connections': [],
			'xmpp_connections': [],
			'xmpp_alt_connections': [],
			'file_server': {},
			'voipDomain': '',
			'voipUserDomain': '',
			'roaming': (1, 1, [(1, 1, 2499999999L, 'EU')], ()),
			'wallet': (False, False)
		}
		self.syncProperties()
		self._cmdQueue = deque()
		self._cmdInProgress = False
		if not len(self.name) > 0:
			ERROR_MSG('Account.__init__ :: username (name) is empty')
			self.name = self.normalizedName.split('@')[0] + str(randint(1000, 9999))
		self.writeToDB()  # all accounts are persistent
	
	def doCmdStr(self, requestID, cmd, str):
		DEBUG_MSG('Server.doCmdStr', requestID, cmd, str)
		self.doCmd(requestID, cmd, str)
	
	def doCmdIntStr(self, requestID, cmd, int, str):
		DEBUG_MSG('Server.doCmdIntStr', requestID, cmd, int, str)
		self.doCmd(requestID, cmd, int, str)
	
	def doCmdInt3(self, requestID, cmd, int1, int2, int3):
		DEBUG_MSG('Server.doCmdInt3', requestID, cmd, int1, int2,
		          int3) if cmd != AccountCommands.CMD_REQ_SERVER_STATS else None
		self.doCmd(requestID, cmd, int1, int2, int3)
	
	def doCmdInt4(self, requestID, cmd, int1, int2, int3, int4):
		DEBUG_MSG('Server.doCmdInt4', requestID, cmd, int1, int2, int3, int4)
		self.doCmd(requestID, cmd, int1, int2, int3, int4)
	
	def doCmdInt2Str(self, requestID, cmd, int1, int2, str):
		DEBUG_MSG('Server.doCmdInt2Str', requestID, cmd, int1, int2, str)
		self.doCmd(requestID, cmd, int1, int2, str)
	
	def doCmdIntArr(self, requestID, cmd, arr):
		DEBUG_MSG('Server.doCmdIntArr', requestID, cmd, arr)
		self.doCmd(requestID, cmd, arr)
	
	def doCmdIntArrStrArr(self, requestID, cmd, intArr, strArr):
		DEBUG_MSG('Server.doCmdIntArrStrArr', requestID, cmd, intArr, strArr)
		self.doCmd(requestID, cmd, intArr, strArr)
	
	def doCmd(self, requestID, cmd, *args):
		# DEBUG_MSG('self._cmdInProgress', self._cmdInProgress, self._cmdQueue)
		if not self.hasClient:
			ERROR_MSG('Server.requestError :: ', requestID, cmd, args)
			return
		if self._cmdInProgress:
			self._cmdQueue.append((requestID, cmd, args))
			DEBUG_MSG('Server.request :: ', requestID, cmd, args, 'queued')
			return
		self.__executeCmd(requestID, cmd, *args)
	
	def __executeCmd(self, requestID, cmd, *args):
		self._cmdInProgress = True
		cmdCall = BASE_REQUESTS.get(cmd)
		try:
			if cmdCall:
				DEBUG_MSG('Server.request :: ', requestID, cmd, args) if cmd != AccountCommands.CMD_REQ_SERVER_STATS else None
				cmdCall(self, requestID, *args)
			else:
				DEBUG_MSG('Server.requestFail (unknown)', requestID, cmd, args)
				self.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, 'Unknown command')
				self.commandFinished_(requestID)
		except AttributeError as a:
			DEBUG_MSG('Server.requestFail :: ', requestID, cmd, args, a)
			self.client.onCmdResponse(requestID, AccountCommands.RES_FAILURE, a.__str__())
			self.commandFinished_(requestID)
		# finally:
		# 	self.__commandFinished()
	
	def commandFinished_(self, requestID):
		self._cmdInProgress = False
		DEBUG_MSG('Request %s finished' % requestID)
		if self._cmdQueue:
			rID, c, a = self._cmdQueue.popleft()
			self.__executeCmd(rID, c, *a)
			# BigWorld.callback(0, lambda : self.__executeCmd(rID, c, *a))
	
	@process
	def syncProperties(self):
		data = yield async(StatsHandler.get_stats, cbname='callback')(self.normalizedName, 'account')
		self.clanDBID = data['account']['clanDBID']
		self.premiumExpiryTime = data['account']['premiumExpiryTime']
		self.autoBanTime = data['account']['autoBanTime']
		self.globalRating = data['account']['globalRating']
		self.attrs = data['account']['attrs']
		del data
	
	def onLogOnAttempt(self, ip, port, password):
		DEBUG_MSG('Account.onLogOnAttempt', ip, port, password)
	
	def set_attrs(self, oldValue):
		DEBUG_MSG('Account.set_attrs', oldValue)
	
	def set_premiumExpiryTime(self, oldValue):
		INFO_MSG('Account.set_premiumExpiryTime', oldValue)
	
	def chatCommandFromClient(self, i1, i2, i3, i4, i5, i6, i7):
		DEBUG_MSG('chatCommandFromClient', i1, i2, i3, i4, i5, i6, i7)
		pass
	
	def inviteCommand(self, i1, i2, i3, i4, i5, i6, i7, i8):
		DEBUG_MSG('inviteCommand', i1, i2, i3, i4, i5, i6, i7, i8)
		pass
	
	def ackCommand(self, i1, i2, i3, i4, i5):
		DEBUG_MSG('ackCommand', i1, i2, i3, i4, i5)
		pass
	
	def onWriteToDB(self, x):
		DEBUG_MSG('onWriteToDB', x, self.name)
	
	def onWriteToDBComplete(self, successful, entity):
		DEBUG_MSG('onWriteToDB', successful, entity)
	
	def onStreamComplete(self, id, success):
		DEBUG_MSG('Account.onStreamComplete', id, success)
		return
	
	def keepAlive(self):
		DEBUG_MSG('Account.keepAlive :: requested')
	
	def onClientDeath(self):
		DEBUG_MSG('Account.onClientDeath : %d' % self.id)
		self.destroy()
	
	def onEnqueued(self, UINT8):
		DEBUG_MSG('Server.onEnqueued', UINT8)
		pass
	
	def onDequeued(self, UINT8):
		DEBUG_MSG('Server.onDequeued', UINT8)
		pass
	
	def onTutorialEnqueued(self, STRING, UINT64):
		DEBUG_MSG('Server.onTutorialEnqueued', STRING, UINT64)
		pass
	
	def onNeedToJoinToUnitMgr(self, MAILBOX, INT32, INT8, UINT16, INT32_2):
		DEBUG_MSG('Server.onNeedToJoinToUnitMgr', MAILBOX, INT32, INT8, UINT16, INT32_2)
		pass
	
	def onArenaCreated(self, MAILBOX, UINT64, OBJECT_ID, UINT8, INT32, UINT8_2):
		DEBUG_MSG('Server.onArenaCreated', MAILBOX, UINT64, OBJECT_ID, UINT8, INT32, UINT8_2)
		pass
	
	def onTutorialCreated(self, MAILBOX, UINT64, OBJECT_ID, UINT8):
		DEBUG_MSG('Server.onTutorialCreated', MAILBOX, UINT64, OBJECT_ID, UINT8)
		pass
	
	def onArenaJoined(self, UINT64, INT32):
		DEBUG_MSG('Server.onArenaJoined', UINT64, INT32)
		pass
	
	def onArenaJoinFailure(self, UINT64, UINT8, STRING):
		DEBUG_MSG('Server.onArenaJoinFailure', UINT64, UINT8, STRING)
		pass
	
	def onPrebattleJoined(self, OBJECT_ID, UINT8, UINT32):
		DEBUG_MSG('Server.onPrebattleJoined', OBJECT_ID, UINT8, UINT32)
		pass
	
	def onPrebattleJoinFailure(self, OBJECT_ID, UINT8):
		DEBUG_MSG('Server.onPrebattleJoinFailure', OBJECT_ID, UINT8)
		pass
	
	def onPrebattleLeft(self, OBJECT_ID):
		DEBUG_MSG('Server.onPrebattleLeft', OBJECT_ID)
		pass
	
	def onKickedFromQueue(self, UINT8):
		DEBUG_MSG('Server.onKickedFromQueue', UINT8)
		pass
	
	def onKickedFromArena(self, UINT64, UINT8):
		DEBUG_MSG('Server.onKickedFromArena', UINT64, UINT8)
		pass
	
	def onKickedFromPrebattle(self, OBJECT_ID, UINT8):
		DEBUG_MSG('Server.onKickedFromPrebattle', OBJECT_ID, UINT8)
		pass
	
	def onVehicleLeftArena(self, INT32, STRING, UINT64, INT32_2, PYTHON, INT32_3, INT64):
		DEBUG_MSG('Server.onVehicleLeftArena', INT32, STRING, UINT64, INT32_2, PYTHON, INT32_3, INT64)
		pass
	
	def onPrebattleResponse(self, OBJECT_ID, INT16, BOOL, STRING, INT32):
		DEBUG_MSG('Server.onPrebattleResponse', OBJECT_ID, INT16, BOOL, STRING, INT32)
		pass
	
	def onPrebattleVehicleChanged(self, OBJECT_ID, INT32, INT32_2):
		DEBUG_MSG('Server.onPrebattleVehicleChanged', OBJECT_ID, INT32, INT32_2)
		pass
	
	def onBattleResultsReceived(self, INT32, STRING):
		DEBUG_MSG('Server.onBattleResultsReceived', INT32, STRING)
		pass
	
	def makeTradeOfferByClient(self, INT16, STRING, UINT16, DB_ID, INT32, INT32_2, INT32_3, INT32_4):
		# Exposed tag
		DEBUG_MSG('Server.makeTradeOfferByClient', INT16, STRING, UINT16, DB_ID, INT32, INT32_2, INT32_3, INT32_4)
		pass
	
	def createTraining(self, INT32, INT32_2, BOOL, STRING):
		# Exposed tag
		DEBUG_MSG('Server.createTraining', INT32, INT32_2, BOOL, STRING)
		pass
	
	def createSquad(self):
		# Exposed tag
		DEBUG_MSG('Server.createSquad')
		pass
	
	def createCompany(self, BOOL, STRING, INT8):
		# Exposed tag
		DEBUG_MSG('Server.createCompany', BOOL, STRING, INT8)
		pass
	
	def createDevPrebattle(self, INT8, INT32, INT32_2, STRING):
		# Exposed tag
		DEBUG_MSG('Server.createDevPrebattle', INT8, INT32, INT32_2, STRING)
		pass
	
	def sendPrebattleInvites(self, ARRAY, STRING):
		# ARRAY is a list of INT64
		# Exposed tag
		DEBUG_MSG('Server.sendPrebattleInvites', ARRAY, STRING)
		pass
	
	def logStreamCorruption(self, INT16, INT32, INT32_2, INT32_3, INT32_4):
		# Exposed tag
		DEBUG_MSG('Server.logStreamCorruption', INT16, INT32, INT32_2, INT32_3, INT32_4)
		pass
	
	def requestToken(self, UINT16, UINT8):
		# Exposed tag
		DEBUG_MSG('Server.requestToken', UINT16, UINT8)
		pass
	
	def receivePrebattleRoster(self, OBJECT_ID, PYTHON):
		DEBUG_MSG('Server.receivePrebattleRoster', OBJECT_ID, PYTHON)
		pass
	
	def updatePrebattle(self, OBJECT_ID, UINT8, STRING):
		DEBUG_MSG('Server.updatePrebattle', OBJECT_ID, UINT8, STRING)
		pass
	
	def addPrebattleInvite(self, OBJECT_ID, INT32, PREBATTLE_INVITE):
		DEBUG_MSG('Server.addPrebattleInvite', OBJECT_ID, INT32, PREBATTLE_INVITE)
		pass
	
	def createAvatar(self, MAILBOX, MAILBOX_2, INT32, UINT8, VECTOR3, FLOAT32, PYTHON, BOOL):
		# TODO: createAvatar
		DEBUG_MSG('Server.createAvatar', MAILBOX, MAILBOX_2, INT32, UINT8, VECTOR3, FLOAT32, PYTHON, BOOL)
		pass
	
	def releaseClientForLogin(self, MAILBOX, PYTHON):
		# sending Account back to Login entity?
		DEBUG_MSG('Server.releaseClientForLogin', MAILBOX, PYTHON)
		pass
	
	def keepAliveFor(self, MAILBOX, INT32, UINT8, UINT16):
		DEBUG_MSG('Server.keepAliveFor', MAILBOX, INT32, UINT8, UINT16)
		pass
	
	def stopKeepingAlive(self, UINT8):
		DEBUG_MSG('Server.stopKeepingAlive', UINT8)
		pass
	
	def kickSelf(self, STRING, BOOL, UINT32):
		DEBUG_MSG('Server.kickSelf', STRING, BOOL, UINT32)
		self.client.onKickedFromServer(STRING, BOOL, UINT32)
		self.destroy()
	
	def destroyIfNoKeepers(self):
		DEBUG_MSG('Server.destroyIfNoKeepers')
		pass
	
	def destroySelfForPeriphery(self, INT32, MAILBOX):
		DEBUG_MSG('Server.destroySelfForPeriphery', INT32, MAILBOX)
		pass
	
	def processInvoices(self):
		DEBUG_MSG('Server.processInvoices')
		pass
	
	def fetchPrebattleAutoInvites(self):
		DEBUG_MSG('Server.fetchPrebattleAutoInvites')
		pass
	
	def setRestriction(self, MAILBOX, INT32, UINT8, STRING, UINT32, UINT32_2, UINT32_3, UINT16, STRING_2, INT32_2,
	                   UINT32_4):
		DEBUG_MSG('Server.setRestriction', MAILBOX, INT32, UINT8, STRING, UINT32, UINT32_2, UINT32_3, UINT16, STRING_2,
		          INT32_2, UINT32_4)
		pass
	
	def setLoginPriority(self, MAILBOX, INT32, ARRAY, ARRAY_2, INT32_2, UINT32):
		# ARRAY is a list of STRING
		# ARRAY_2 is a list of STRING
		DEBUG_MSG('Server.setLoginPriority', MAILBOX, INT32, ARRAY, ARRAY_2, INT32_2, UINT32)
		pass
	
	def delRestriction(self, MAILBOX, INT32, UINT8, UINT64, INT32_2, UINT32):
		DEBUG_MSG('Server.delRestriction', MAILBOX, INT32, UINT8, UINT64, INT32_2, UINT32)
		pass
	
	def setType(self, MAILBOX, INT32, INT16, INT16_2, INT32_2, UINT32):
		DEBUG_MSG('Server.setType', MAILBOX, INT32, INT16, INT16_2, INT32_2, UINT32)
		pass
	
	def changeFairPlay(self, MAILBOX, INT32, STRING, INT32_2, INT32_3, UINT32, INT32_4, UINT32_2):
		DEBUG_MSG('Server.changeFairPlay', MAILBOX, INT32, STRING, INT32_2, INT32_3, UINT32, INT32_4, UINT32_2)
		pass
	
	def excludeFromFairPlay(self, MAILBOX, INT32, BOOL, INT32_2, UINT32):
		DEBUG_MSG('Server.excludeFromFairPlay', MAILBOX, INT32, BOOL, INT32_2, UINT32)
		pass
	
	def setFinPassword(self, MAILBOX, INT32, STRING, STRING_2, BOOL, INT32_2, UINT32):
		DEBUG_MSG('Server.setFinPassword', MAILBOX, INT32, STRING, STRING_2, BOOL, INT32_2, UINT32)
		pass
	
	def setAutoBanTime(self, MAILBOX, INT32, UINT32, INT32_2, UINT32_2):
		DEBUG_MSG('Server.setAutoBanTime', MAILBOX, INT32, UINT32, INT32_2, UINT32_2)
		pass
	
	def setNextBanLevel(self, MAILBOX, INT32, STRING, UINT8, INT32_2, UINT32):
		DEBUG_MSG('Server.setNextBanLevel', MAILBOX, INT32, STRING, UINT8, INT32_2, UINT32)
		pass
	
	def lockVehicleType(self, MAILBOX, INT32, PYTHON, PYTHON_2, INT32_2, UINT32):
		DEBUG_MSG('Server.lockVehicleType', MAILBOX, INT32, PYTHON, PYTHON_2, INT32_2, UINT32)
		pass
	
	def unlockVehicleType(self, MAILBOX, INT32, PYTHON, PYTHON_2, INT32_2, UINT32):
		DEBUG_MSG('Server.unlockVehicleType', MAILBOX, INT32, PYTHON, PYTHON_2, INT32_2, UINT32)
		pass
	
	def processEBankResponse(self, MAILBOX, INT32, INT8, INT32_2, INT32_3, STRING):
		DEBUG_MSG('Server.processEBankResponse', MAILBOX, INT32, INT8, INT32_2, INT32_3, STRING)
		pass
	
	def addRemoveRareAchievements(self, MAILBOX, INT32, ARRAY, INT32_2, UINT32):
		# ARRAY is a list of INT32
		DEBUG_MSG('Server.addRemoveRareAchievements', MAILBOX, INT32, ARRAY, INT32_2, UINT32)
		pass
	
	def restoreAccountFromPoint(self, MAILBOX, INT32, UINT64, PYTHON, ARRAY, UINT64_2, UINT32, UINT64_3, UINT64_4,
	                            INT32_2, UINT32_2):
		# ARRAY is a list of UINT64
		DEBUG_MSG('Server.restoreAccountFromPoint', MAILBOX, INT32, UINT64, PYTHON, ARRAY, UINT64_2, UINT32, UINT64_3,
		          UINT64_4, INT32_2, UINT32_2)
		pass
	
	def processSessionTrackerData(self, MAILBOX, INT32, UINT8, STRING):
		DEBUG_MSG('Server.processSessionTrackerData', MAILBOX, INT32, UINT8, STRING)
		pass
	
	def contributeXPToReferrer(self, MAILBOX, INT32, STRING, DB_ID, STRING_2, DB_ID_2, PYTHON):
		DEBUG_MSG('Server.contributeXPToReferrer', MAILBOX, INT32, STRING, DB_ID, STRING_2, DB_ID_2, PYTHON)
		pass
	
	def addReferral(self, MAILBOX, INT32, DB_ID, PYTHON):
		DEBUG_MSG('Server.addReferral', MAILBOX, INT32, DB_ID, PYTHON)
		pass
	
	def delReferral(self, MAILBOX, INT32, DB_ID):
		DEBUG_MSG('Server.delReferral', MAILBOX, INT32, DB_ID)
		pass
	
	def sendPropertiesTo(self, MAILBOX, INT32, ARRAY):
		# ARRAY is a list of STRING
		DEBUG_MSG('Server.sendPropertiesTo', MAILBOX, INT32, ARRAY)
		pass
	
	def wipe(self, MAILBOX, INT32, BOOL, INT32_2, UINT32):
		DEBUG_MSG('Server.wipe', MAILBOX, INT32, BOOL, INT32_2, UINT32)
		pass
	
	def resetDailyLimits(self, MAILBOX, INT32, ARRAY, INT32_2, UINT32):
		# ARRAY is a list of UINT8
		DEBUG_MSG('Server.resetDailyLimits', MAILBOX, INT32, ARRAY, INT32_2, UINT32)
		pass
	
	def setPlayLimits(self, MAILBOX, INT32, INT32_2, STRING, INT32_3, STRING_2, INT32_4, UINT32):
		DEBUG_MSG('Server.setPlayLimits', MAILBOX, INT32, INT32_2, STRING, INT32_3, STRING_2, INT32_4, UINT32)
		pass
	
	def processSpaAttributes(self, MAILBOX, INT32, INT32_2, PYTHON):
		DEBUG_MSG('Server.processSpaAttributes', MAILBOX, INT32, INT32_2, PYTHON)
		pass
	
	def processWalletResponse(self, MAILBOX, INT32, PYTHON):
		DEBUG_MSG('Server.processWalletResponse', MAILBOX, INT32, PYTHON)
		pass
	
	def processIGRData(self, MAILBOX, INT32, PYTHON):
		DEBUG_MSG('Server.processIGRData', MAILBOX, INT32, PYTHON)
		pass
	
	def exportToWeb(self):
		DEBUG_MSG('Server.exportToWeb')
		pass
	
	def syncWallet(self):
		DEBUG_MSG('Server.syncWallet')
		pass
	
	def resetWalletIDs(self, MAILBOX, INT32, UINT64, UINT64_2, INT32_2, UINT32):
		DEBUG_MSG('Server.resetWalletIDs', MAILBOX, INT32, UINT64, UINT64_2, INT32_2, UINT32)
		pass
	
	def resetWalletAssets(self, MAILBOX, INT32, INT64, INT64_2, UINT32, INT32_2, UINT32_2):
		DEBUG_MSG('Server.resetWalletAssets', MAILBOX, INT32, INT64, INT64_2, UINT32, INT32_2, UINT32_2)
		pass
	
	def extraWriteToDB(self, BOOL):
		DEBUG_MSG('Server.extraWriteToDB', BOOL)
		pass
	
	def createClan(self, MAILBOX, INT32, STRING, STRING_2, STRING_3, STRING_4, INT32_2, INT32_3, UINT32):
		DEBUG_MSG('Server.createClan', MAILBOX, INT32, STRING, STRING_2, STRING_3, STRING_4, INT32_2, INT32_3, UINT32)
		pass
	
	def enterLeaveClan(self, MAILBOX, INT32, DB_ID, DB_ID_2, UINT8, INT32_2, UINT32):
		DEBUG_MSG('Server.enterLeaveClan', MAILBOX, INT32, DB_ID, DB_ID_2, UINT8, INT32_2, UINT32)
		pass
	
	def receiveClanMemberInfo(self, DB_ID, DB_ID_2, STRING, STRING_2, STRING_3, STRING_4, DB_ID_3, INT32, INT32_2,
	                          STRING_5, STRING_6):
		DEBUG_MSG('Server.receiveClanMemberInfo', DB_ID, DB_ID_2, STRING, STRING_2, STRING_3, STRING_4, DB_ID_3, INT32,
		          INT32_2, STRING_5, STRING_6)
		pass
	
	def receiveClanMembersListDiff(self, DB_ID, STRING):
		DEBUG_MSG('Server.receiveClanMembersListDiff', DB_ID, STRING)
		pass
	
	def callFortMethod(self, INT64, INT32, INT64_2, INT64_3, INT64_4):
		DEBUG_MSG('Server.callFortMethod', INT64, INT32, INT64_2, INT64_3, INT64_4)
		# Exposed tag
		pass
	
	def onFortReply(self, INT64, INT32, STRING):
		DEBUG_MSG('Server.onFortReply', INT64, INT32, STRING)
		pass
	
	def onFortUpdate(self, STRING, STRING_2, BOOL):
		DEBUG_MSG('Server.onFortUpdate', STRING, STRING_2, BOOL)
		pass
	
	def onPickupEquipments(self, INT64, INT32, INT64_2, INT64_3, INT64_4, INT64_5, INT64_6):
		DEBUG_MSG('Server.onPickupEquipments', INT64, INT32, INT64_2, INT64_3, INT64_4, INT64_5, INT64_6)
		pass
	
	def onFortBattleRoundEnd(self, STRING):
		DEBUG_MSG('Server.onFortBattleRoundEnd', STRING)
		pass
	
	def onFortBattleEnd(self, STRING):
		DEBUG_MSG('Server.onFortBattleEnd', STRING)
		pass
	
	def onFortNotification(self, INT64, INT64_2, PYTHON):
		DEBUG_MSG('Server.onFortNotification', INT64, INT64_2, PYTHON)
		pass
	
	def requestFortPublicInfo(self, INT32, INT8, STRING, INT16, INT8_2, INT8_3, INT8_4, INT8_5, INT8_6, INT8_7, INT8_8,
	                          INT32_2, INT8_9, INT8_10, INT32_3, INT8_11, INT32_4, INT8_12, INT32_5, BOOL, ARRAY):
		# ARRAY is a list of INT64
		# Exposed tag
		DEBUG_MSG('Server.requestFortPublicInfo', INT32, INT8, STRING, INT16, INT8_2, INT8_3, INT8_4, INT8_5, INT8_6,
		          INT8_7, INT8_8, INT32_2, INT8_9, INT8_10, INT32_3, INT8_11, INT32_4, INT8_12, INT32_5, BOOL, ARRAY)
		pass
	
	def debugRunMethod(self, STRING, PYTHON):
		DEBUG_MSG('Server.debugRunMethod', STRING, PYTHON)
		pass
	
	def setToken(self, INT64, INT32):
		DEBUG_MSG('Server.setToken', INT64, INT32)
		pass
	
	def updateVehDossiersCut(self):
		DEBUG_MSG('Server.updateVehDossiersCut')
		pass
	
	def updateVehicleDossiers(self):
		DEBUG_MSG('Server.updateVehicleDossiers')
		pass
	
	def createUnitMgr(self, INT32, INT32_2):
		# Exposed tag
		DEBUG_MSG('Server.createUnitMgr', INT32, INT32_2)
		pass
	
	def createClubUnitMgr(self, INT32, INT32_2, UINT64, PYTHON, STRING):
		DEBUG_MSG('Server.createClubUnitMgr', INT32, INT32_2, UINT64, PYTHON, STRING)
		pass
	
	def joinClubUnitMgr(self, INT32, UINT64, UINT64_2, PYTHON):
		DEBUG_MSG('Server.joinClubUnitMgr', INT32, UINT64, UINT64_2, PYTHON)
		pass
	
	def joinUnit(self, INT32, UINT64, INT32_2, INT32_3):
		# Exposed tag
		DEBUG_MSG('Server.joinUnit', INT32, UINT64, INT32_2, INT32_3)
		pass
	
	def doUnitCmd(self, INT32, INT32_2, UINT64, INT32_3, UINT64_2, INT32_4, STRING):
		# Exposed tag
		DEBUG_MSG('Server.doUnitCmd', INT32, INT32_2, UINT64, INT32_3, UINT64_2, INT32_4, STRING)
		pass
	
	def sendUnitInvites(self, INT32, ARRAY, STRING):
		# ARRAY is a list of INT64
		# Exposed tag
		DEBUG_MSG('Server.sendUnitInvites', INT32, ARRAY, STRING)
		pass
	
	def sendFortBattleInvites(self, ARRAY, UINT64, PREBATTLE_INVITE):
		# ARRAY is a list of INT64
		DEBUG_MSG('Server.sendFortBattleInvites', ARRAY, UINT64, PREBATTLE_INVITE)
		pass
	
	def onUnitJoin(self, INT32, MAILBOX, INT32_2, INT32_3, UINT64, PYTHON):
		DEBUG_MSG('Server.onUnitJoin', INT32, MAILBOX, INT32_2, INT32_3, UINT64, PYTHON)
		pass
	
	def onUnitLeave(self, INT32, INT32_2, UINT64, INT32_3):
		DEBUG_MSG('Server.onUnitLeave', INT32, INT32_2, UINT64, INT32_3)
		pass
	
	def onUnitCall(self, INT32, INT32_2, UINT64, INT32_3, STRING, PYTHON):
		DEBUG_MSG('Server.onUnitCall', INT32, INT32_2, UINT64, INT32_3, STRING, PYTHON)
		pass
	
	def onUnitNotify(self, UINT64, INT32, INT32_2, PYTHON):
		DEBUG_MSG('Server.onUnitNotify', UINT64, INT32, INT32_2, PYTHON)
		pass
	
	def onUnitChangedLeader(self, MAILBOX, BOOL):
		DEBUG_MSG('Server.onUnitChangedLeader', MAILBOX, BOOL)
		pass
	
	def onUnitExtrasUpdated(self, INT32, INT32_2, PYTHON):
		DEBUG_MSG('Server.onUnitExtrasUpdated', INT32, INT32_2, PYTHON)
		pass
	
	def sendUnitUpdate(self, UINT64, INT32, STRING, STRING_2):
		DEBUG_MSG('Server.sendUnitUpdate', UINT64, INT32, STRING, STRING_2)
		pass
	
	def setAllRosterSlots(self, INT32, UINT64, INT32_2, ARRAY, ARRAY_2):
		# ARRAY is a list of INT32
		# ARRAY_2 is a list of STRING
		# Exposed tag
		DEBUG_MSG('Server.setAllRosterSlots', INT32, UINT64, INT32_2, ARRAY, ARRAY_2)
		pass
	
	def subscribeUnitBrowser(self, INT16, BOOL):
		# Exposed tag
		DEBUG_MSG('Server.subscribeUnitBrowser', INT16, BOOL)
		pass
	
	def unsubscribeUnitBrowser(self):
		# Exposed tag
		DEBUG_MSG('Server.unsubscribeUnitBrowser')
		pass
	
	def recenterUnitBrowser(self, INT32, INT16, BOOL):
		# Exposed tag
		DEBUG_MSG('Server.recenterUnitBrowser', INT32, INT16, BOOL)
		pass
	
	def doUnitBrowserCmd(self, INT32):
		# Exposed tag
		DEBUG_MSG('Server.doUnitBrowserCmd', INT32)
		pass
	
	def onUnitBrowserError(self, INT32, STRING):
		DEBUG_MSG('Server.onUnitBrowserError', INT32, STRING)
		pass
	
	def onUnitBrowserResultsSet(self, STRING):
		DEBUG_MSG('Server.onUnitBrowserResultsSet', STRING)
		pass
	
	def onUnitBrowserResultsUpdate(self, STRING):
		DEBUG_MSG('Server.onUnitBrowserResultsUpdate', STRING)
		pass
	
	def acceptUnitAutoSearch(self, UINT64, INT32):
		# Exposed tag
		DEBUG_MSG('Server.acceptUnitAutoSearch', UINT64, INT32)
		pass
	
	def onSendPrebattleInvites(self, DB_ID, STRING, DB_ID_2, STRING_2, UINT64, UINT8):
		DEBUG_MSG('Server.onSendPrebattleInvites', DB_ID, STRING, DB_ID_2, STRING_2, UINT64, UINT8)
		pass
	
	def receiveClubResponse(self, UINT8, INT64, INT16, STRING, STRING_2):
		DEBUG_MSG('Server.receiveClubResponse', UINT8, INT64, INT16, STRING, STRING_2)
		pass
	
	def receiveClubUpdate(self, UINT8, INT64, DB_ID, STRING, STRING_2):
		DEBUG_MSG('Server.receiveClubUpdate', UINT8, INT64, DB_ID, STRING, STRING_2)
		pass
	
	def receiveServerClubResponse(self, UINT8, INT16, STRING):
		DEBUG_MSG('Server.receiveServerClubResponse', UINT8, INT16, STRING)
		pass
	
	def receiveClubNotification(self, STRING):
		DEBUG_MSG('Server.receiveClubNotification', STRING)
		pass
	
	def forceCheckinClub(self, DB_ID):
		DEBUG_MSG('Server.forceCheckinClub', DB_ID)
		pass
	
	def receiveExternalNotification(self, PYTHON):
		DEBUG_MSG('Server.receiveExternalNotification', PYTHON)
		pass
	
	def sendExternalNotificationReply(self, INT64, STRING, UINT8):
		DEBUG_MSG('Server.sendExternalNotificationReply', INT64, STRING, UINT8)
		pass


PlayerAccount = Account
