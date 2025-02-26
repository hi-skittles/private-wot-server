# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/UnitBase.py
# Compiled at: 2015-04-25 07:58:30
import struct
from constants import VEHICLE_CLASS_INDICES, PREBATTLE_TYPE
from items import vehicles
from UnitRoster import UnitRoster, BaseUnitRosterSlot, _getVehClassTag, _BAD_CLASS_INDEX
from UnitRoster import buildNamesDict, _reprBitMaskFromDict
from UnitRoster import SortieRoster6, SortieRoster8, SortieRoster10, FortRoster10, ClubRoster
from ops_pack import OpsUnpacker, packPascalString, unpackPascalString, initOpsFormatDef
from unit_helpers.ExtrasHandler import EmptyExtrasHandler, FortBattleExtrasHandler
from unit_helpers.ExtrasHandler import ClubExtrasHandler, SortieExtrasHandler
from debug_utils import LOG_DAN, LOG_SVAN_DEV

class UNIT_STATE:
    LOCKED = 1
    INVITE_ONLY = 2
    IN_QUEUE = 4
    IN_SEARCH = 8
    DEV_MODE = 16
    IN_ARENA = 32
    IN_PRE_ARENA = 256
    IN_ROSTER_WAIT = 512
    DEFAULT = 0
    PRE_QUEUE = 0
    PRE_SEARCH = 0
    MODAL_STATES = IN_QUEUE | IN_SEARCH | IN_ARENA
    CHANGING_TO_ARENA = IN_QUEUE | IN_ARENA | IN_PRE_ARENA
    CHANGED_STATE_ASQ = IN_ARENA | IN_PRE_ARENA | IN_SEARCH | IN_QUEUE


UNIT_STATE_NAMES = buildNamesDict(UNIT_STATE)

class UNIT_BROWSER_TYPE:
    NOT_RATED_UNITS = 1
    RATED_CLUBS = 2
    ALL = NOT_RATED_UNITS | RATED_CLUBS


UNIT_BROWSER_TYPE_NAMES = buildNamesDict(UNIT_BROWSER_TYPE)

class UNIT_ERROR:
    OK = 0
    ALREADY_JOINED_UNIT = 1
    UNIT_MGR_ENTITY_CREATION_FAIL = 2
    UNIT_ADD_FAIL = 3
    CANT_FIND_UNIT_MGR = 4
    ADD_PLAYER_FAIL = 5
    NO_UNIT_MGR = 6
    WRONG_UNIT_REQUISITES = 7
    REMOVE_PLAYER_FAIL = 8
    GET_VEHICLE_FAIL = 9
    ADD_MEMBER_FAIL = 10
    SET_MEMBER_READY_FAIL = 11
    ASSIGN_MEMBER_FAIL = 12
    FAIL_UNIT_METHOD = 13
    BAD_SLOT_IDX = 14
    INSUFFICIENT_ROLE = 15
    NO_UNIT = 16
    BAD_ROSTER_PACK = 17
    TOO_MANY_ROSTERS = 18
    JOIN_CTX_LOCK = 19
    CANT_INVITE = 20
    TIMEOUT = 21
    NOT_READY = 22
    NOT_IN_QUEUE = 23
    NOT_IDLE = 24
    NOT_IN_SEARCH = 25
    BAD_JOINING_ACC = 26
    PLAYER_IGNORED = 27
    NOT_INVITED = 28
    REMOVED_PLAYER = 29
    OFFLINE_PLAYER = 30
    KICKED_PLAYER = 31
    UNIT_RESTORED = 32
    ACCOUNT_RESTORED = 33
    GET_READY_VEHICLE_FAIL = 34
    COOLDOWN = 35
    UNIT_ASSEMBLER_TIMEOUT = 36
    ALREADY_INVITED = 37
    HAS_IN_ARENA_MEMBERS = 38
    KICKED_CANDIDATE = 39
    INVITE_REMOVED = 40
    BAD_ACCOUNT_TYPE = 41
    BAD_POINTS_SUM = 42
    WAITING_FOR_JOIN = 43
    BAD_VEHICLE_LEVEL = 44
    CLAN_CHANGED = 45
    NO_CLAN_MEMBERS = 46
    BAD_CLAN = 47
    NO_PLAYER = 48
    SLOT_RESERVED = 49
    SLOT_OCCUPIED = 50
    TOO_MANY_CLOSED_SLOTS = 51
    SLOT_NOT_CLOSED = 52
    CANT_PICK_LEADER = 53
    RESTRICT_LEGIONARIES = 54
    RESTRICT_INVITED = 55
    VEHICLE_MISMATCH = 56
    NO_VEHICLES = 57
    TOO_MANY_LEGIONARIES = 58
    VEHICLE_NOT_CHOSEN = 59
    ALREADY_IN_SLOT = 60
    FORT_BATTLE_END = 61
    NO_AVAILABLE_SLOTS = 62
    TOO_FEW_POINTS = 63
    BAD_DIVISION = 64
    CANT_CHANGE_DIVISION = 65
    CANNOT_LEAD = 66
    CLUB_CHECKOUT_FAIL = 67
    WRONG_UNITMGR = 68
    LEGIONARIES_FORBIDDEN = 69
    PREV_RATED_BATTLE_IN_PROGRESS = 70
    OFF_SEASON = 71
    BAD_PARAMS = 72


OK = UNIT_ERROR.OK

class UNIT_SLOT:
    ANY = -1
    REMOVE = -2


INV_ID_CLEAR_VEHICLE = 0
LEADER_SLOT = 0

class UNIT_OP:
    SET_VEHICLE = 1
    SET_MEMBER = 2
    DEL_MEMBER = 3
    ADD_PLAYER = 4
    REMOVE_PLAYER = 5
    READY_MASK = 6
    SET_SLOT = 7
    CLEAR_VEHICLE = 8
    VEHICLE_DICT = 9
    UNIT_STATE = 10
    CLOSE_SLOT = 11
    OPEN_SLOT = 12
    SET_COMMENT = 13
    CHANGE_ROLE = 14
    MODAL_TIMESTAMP = 15
    GIVE_LEADERSHIP = 16
    CHANGE_DIVISION = 17
    EXTRAS_UPDATE = 18
    EXTRAS_RESET = 19


class UNIT_ROLE:
    DEFAULT = 0
    INVITED = 1
    COMMANDER_UPDATES = 2
    CHANGE_ROSTER = 4
    LEGIONARY = 16
    MANAGER = 32
    IN_ARENA = 64
    OFFLINE = 128
    CAN_LEAD = 256
    START_STOP_BATTLE = CHANGE_ROSTER
    ADD_REMOVE_MEMBERS = CHANGE_ROSTER
    INVITE_KICK_PLAYERS = CHANGE_ROSTER
    CREATOR = COMMANDER_UPDATES | CHANGE_ROSTER
    CHANGE_LEADERSHIP = CREATOR | MANAGER
    SOCIAL_ROLES = LEGIONARY | MANAGER | CAN_LEAD
    SELF_ONLY = 65536
    SELF_UNLOCKED = 131072
    NON_IDLE = 262144
    NO_LEGIONARY_CANDIDATES = 524288
    PRE_ARENA = 1048576


UNIT_ROLE_NAMES = buildNamesDict(UNIT_ROLE)
VEHICLE_CLASS_SPG = VEHICLE_CLASS_INDICES.get('SPG', _BAD_CLASS_INDEX)

class UNIT_BROWSER_CMD:
    REFRESH = 0
    LEFT = 1
    RIGHT = 2


class UNIT_BROWSER_ERROR:
    OK = 0
    UNSUBSCRIBED = 1
    PAGING_ERROR = 2
    ACCEPT_TIMEOUT = 3
    BAD_ACCEPT_CONTEXT = 4
    SEARCH_CANCELED = 5
    ACCEPT_CANCELED = 6
    ALREADY_SUBSCRIBED = 7
    NOT_SUBSCRIBED = 8
    SERVICE_UNAVAILABLE = 9


class UNIT_PUBLISHER_ERROR:
    OK = 0
    ALREADY_PUBLISHED = 1
    NOT_PUBLISHED = 2


class UNIT_NOTIFY_CMD:
    SET_VEHICLE = 1
    PLAYER_ONLINE = 2
    TRANSFER_LEADERSHIP = 3
    PUBLISH_STATE_CHANGE = 4
    SET_MEMBER_READY = 5
    KICK_ALL = 6
    EXTRAS_UPDATED = 7
    ROSTER_CONFIRM = 8


class CLIENT_UNIT_CMD:
    NONE = 0
    LEAVE_UNIT = 1
    START_UNIT_BATTLE = 2
    STOP_UNIT_BATTLE = 3
    START_AUTO_SEARCH = 4
    STOP_AUTO_SEARCH = 5
    SET_UNIT_MEMBER = 6
    SET_UNIT_VEHICLE = 7
    FIT_UNIT_MEMBER = 8
    ASSIGN_UNIT_MEMBER = 9
    REASSIGN_UNIT_MEMBER = 10
    SET_UNIT_MEMBER_READY = 11
    KICK_UNIT_PLAYER = 12
    LOCK_UNIT = 13
    OPEN_UNIT = 14
    CLOSE_UNIT_SLOT = 15
    SET_ROSTER_SLOT = 16
    SET_UNIT_COMMENT = 17
    SET_UNIT_DEV_MODE = 18
    GIVE_LEADERSHIP = 19
    CHANGE_SORTIE_DIVISION = 20
    SET_RATED_BATTLE = 21


class UNIT_NOTIFY_ID:
    PARENT_UNIT_MGR = -1


class UNIT_MGR_FLAGS:
    DEFAULT = 0
    SORTIE = 1
    DOUBLE_UNIT = 2
    SORTIE_DIVISION_6 = 4
    SORTIE_DIVISION_8 = 8
    DIVISION_FLAG_MASK = SORTIE | SORTIE_DIVISION_8 | SORTIE_DIVISION_6
    FORT_BATTLE = 16
    CLUBS = 32


class ROSTER_TYPE:
    UNIT_ROSTER = 0
    SORTIE_ROSTER_6 = UNIT_MGR_FLAGS.SORTIE | UNIT_MGR_FLAGS.SORTIE_DIVISION_6
    SORTIE_ROSTER_8 = UNIT_MGR_FLAGS.SORTIE | UNIT_MGR_FLAGS.SORTIE_DIVISION_8
    SORTIE_ROSTER_10 = UNIT_MGR_FLAGS.SORTIE
    FORT_ROSTER_10 = UNIT_MGR_FLAGS.FORT_BATTLE
    CLUB_ROSTER_10 = UNIT_MGR_FLAGS.CLUBS
    _MASK = UNIT_MGR_FLAGS.SORTIE | UNIT_MGR_FLAGS.SORTIE_DIVISION_8 | UNIT_MGR_FLAGS.SORTIE_DIVISION_6 | UNIT_MGR_FLAGS.FORT_BATTLE | CLUB_ROSTER_10


class EXTRAS_HANDLER_TYPE:
    EMPTY = 0
    FORT_BATTLE = 1
    CLUBS = 2
    SORTIE = 3


class SORTIE_DIVISION(object):
    MIDDLE = 6
    CHAMPION = 8
    ABSOLUTE = 10
    _ORDER = (MIDDLE, CHAMPION, ABSOLUTE)


SORTIE_DIVISION_NAMES = dict([ (v, k) for k, v in SORTIE_DIVISION.__dict__.iteritems() if not k.startswith('_') ])
SORTIE_DIVISION_LEVEL_TO_FLAGS = {SORTIE_DIVISION.MIDDLE: ROSTER_TYPE.SORTIE_ROSTER_6,
 SORTIE_DIVISION.CHAMPION: ROSTER_TYPE.SORTIE_ROSTER_8,
 SORTIE_DIVISION.ABSOLUTE: ROSTER_TYPE.SORTIE_ROSTER_10}
SORTIE_DIVISION_NAME_TO_FLAGS = dict([ (v, SORTIE_DIVISION_LEVEL_TO_FLAGS[k]) for k, v in SORTIE_DIVISION_NAMES.iteritems() ])
SORTIE_DIVISION_FLAGS_TO_NAME = dict([ (flags, name) for name, flags in SORTIE_DIVISION_NAME_TO_FLAGS.iteritems() ])
ROSTER_TYPE_TO_CLASS = {ROSTER_TYPE.UNIT_ROSTER: UnitRoster,
 ROSTER_TYPE.SORTIE_ROSTER_6: SortieRoster6,
 ROSTER_TYPE.SORTIE_ROSTER_8: SortieRoster8,
 ROSTER_TYPE.SORTIE_ROSTER_10: SortieRoster10,
 ROSTER_TYPE.FORT_ROSTER_10: FortRoster10,
 ROSTER_TYPE.CLUB_ROSTER_10: ClubRoster}
EXTRAS_HANDLER_TYPE_TO_HANDLER = {EXTRAS_HANDLER_TYPE.EMPTY: EmptyExtrasHandler,
 EXTRAS_HANDLER_TYPE.FORT_BATTLE: FortBattleExtrasHandler,
 EXTRAS_HANDLER_TYPE.CLUBS: ClubExtrasHandler,
 EXTRAS_HANDLER_TYPE.SORTIE: SortieExtrasHandler}

class UnitBase(OpsUnpacker):
    _opsFormatDefs = initOpsFormatDef({UNIT_OP.SET_VEHICLE: ('qHi', '_setVehicle'),
     UNIT_OP.SET_MEMBER: ('qB', '_setMember'),
     UNIT_OP.DEL_MEMBER: ('B', '_delMemberBySlot'),
     UNIT_OP.ADD_PLAYER: ('', '_unpackPlayer'),
     UNIT_OP.REMOVE_PLAYER: ('q', '_removePlayer'),
     UNIT_OP.READY_MASK: ('H', '_setReadyMask'),
     UNIT_OP.SET_SLOT: ('', '_unpackRosterSlot'),
     UNIT_OP.CLEAR_VEHICLE: ('q', '_clearVehicle'),
     UNIT_OP.VEHICLE_DICT: ('', '_unpackVehicleDict'),
     UNIT_OP.UNIT_STATE: ('H', '_setUnitState'),
     UNIT_OP.CLOSE_SLOT: ('B', '_closeSlot'),
     UNIT_OP.OPEN_SLOT: ('B', '_openSlot'),
     UNIT_OP.SET_COMMENT: ('',
                           'setComment',
                           'S',
                           ['']),
     UNIT_OP.CHANGE_ROLE: ('qH', '_changePlayerRole'),
     UNIT_OP.MODAL_TIMESTAMP: ('i', '_setModalTimestamp'),
     UNIT_OP.GIVE_LEADERSHIP: ('Q', '_giveLeadership'),
     UNIT_OP.CHANGE_DIVISION: ('i', '_changeSortieDivision'),
     UNIT_OP.EXTRAS_UPDATE: ('',
                             'onUnitExtrasUpdate',
                             'S',
                             ['']),
     UNIT_OP.EXTRAS_RESET: (None, 'resetExtras')})
    MAX_PLAYERS = 250

    def __init__(self, slotDefs={}, slotCount=0, packedRoster='', extras='', packedUnit='', rosterTypeID=ROSTER_TYPE.UNIT_ROSTER, extrasHandlerID=EXTRAS_HANDLER_TYPE.EMPTY, prebattleTypeID=PREBATTLE_TYPE.UNIT):
        if packedUnit:
            self.unpack(packedUnit)
        else:
            self._rosterTypeID = rosterTypeID
            self._prebattleTypeID = prebattleTypeID
            RosterType = ROSTER_TYPE_TO_CLASS.get(rosterTypeID)
            if slotDefs and not slotCount:
                slotCount = len(slotDefs)
            self._roster = RosterType(slotDefs, slotCount, packedRoster)
            self._freeSlots = set(xrange(0, slotCount))
            self._dirty = 1
            self._state = UNIT_STATE.DEFAULT
            self._extrasHandlerID = extrasHandlerID
            eHandler = self._extrasHandler = EXTRAS_HANDLER_TYPE_TO_HANDLER[extrasHandlerID](self)
            newExtras = eHandler.new()
            if extras:
                unpackedExtras = eHandler.unpack(extras)
                if unpackedExtras:
                    newExtras.update(unpackedExtras)
            self._extras = newExtras
            self._initClean()

    def _initClean(self):
        self._members = {}
        self._vehicles = {}
        self._players = {}
        self._playerSlots = {}
        self._readyMask = 0
        self._fullReadyMask = 0
        self._strComment = ''
        self._packedOps = ''
        self._packedCmdrOps = ''
        self._closedSlotMask = 0
        self._notifications = []
        self._reservedSlots = set()
        self._modalTimestamp = 0

    def _setVehicle(self, playerID, vehTypeCompDescr, vehInvID):
        veh = self._vehicles.get(playerID)
        if not veh or veh['vehTypeCompDescr'] != vehTypeCompDescr:
            itemTypeIdx, nationIdx, inNationIdx = vehicles.parseIntCompactDescr(vehTypeCompDescr)
            vehType = vehicles.g_cache.vehicle(nationIdx, inNationIdx)
            classTag = _getVehClassTag(vehType)
            vehClassIdx = VEHICLE_CLASS_INDICES.get(classTag, _BAD_CLASS_INDEX)
            self._vehicles[playerID] = dict(vehTypeCompDescr=vehTypeCompDescr, vehInvID=vehInvID, nationIdx=nationIdx, inNationIdx=inNationIdx, vehLevel=vehType.level, vehClassIdx=vehClassIdx)
            self.storeOp(UNIT_OP.SET_VEHICLE, playerID, vehTypeCompDescr, vehInvID)
            self._storeNotification(playerID, UNIT_NOTIFY_CMD.SET_VEHICLE, [vehInvID])
            self._dirty = 1
            return True
        return False

    def _clearVehicle(self, playerID):
        self._vehicles.pop(playerID, None)
        slotIdx = self._playerSlots.get(playerID)
        if slotIdx is not None:
            self.setMemberReady(playerID, False)
        self._dirty = 1
        self.storeOp(UNIT_OP.CLEAR_VEHICLE, playerID)
        self._storeNotification(playerID, UNIT_NOTIFY_CMD.SET_VEHICLE, [0])
        return

    def _setMember(self, playerID, slotChosenIdx):
        member = dict(playerID=playerID, slotIdx=slotChosenIdx)
        self._members[slotChosenIdx] = member
        self._freeSlots.discard(slotChosenIdx)
        self._playerSlots[playerID] = slotChosenIdx
        self._fullReadyMask |= 1 << slotChosenIdx
        self.storeOp(UNIT_OP.SET_MEMBER, playerID, slotChosenIdx)
        self._dirty = 1

    def _delMemberBySlot(self, slotIdx):
        member = self._members.get(slotIdx, None)
        if not member:
            return UNIT_ERROR.FAIL_UNIT_METHOD
        else:
            playerID = member['playerID']
            self.setMemberReady(playerID, False)
            self._members.pop(slotIdx)
            self._freeSlots.add(slotIdx)
            self._playerSlots.pop(playerID, None)
            clearMask = ~(1 << slotIdx)
            self._fullReadyMask &= clearMask
            self._dirty = 1
            self.storeOp(UNIT_OP.DEL_MEMBER, slotIdx)
            return OK

    def _addPlayer(self, playerID, **kwargs):
        self._players[playerID] = kwargs
        self._dirty = 1
        packed = struct.pack(self._PLAYER_DATA, playerID, kwargs.get('accountID', 0), kwargs.get('timeJoin', 0), kwargs.get('role', 0), kwargs.get('igrType', 0), kwargs.get('rating', 0), kwargs.get('peripheryID', 0))
        packed += packPascalString(kwargs.get('nickName', ''))
        packed += packPascalString(kwargs.get('clanAbbrev', ''))
        self._appendOp(UNIT_OP.ADD_PLAYER, packed)

    def _removePlayer(self, playerID):
        self._players.pop(playerID, None)
        self._vehicles.pop(playerID, None)
        self._dirty = 1
        self.storeOp(UNIT_OP.REMOVE_PLAYER, playerID)
        return

    def _changePlayerRole(self, playerID, roleFlags):
        playerData = self._players.get(playerID)
        if playerData:
            playerData['role'] = roleFlags
            self._dirty = 1
            self.storeOp(UNIT_OP.CHANGE_ROLE, playerID, roleFlags)

    def _setRosterSlot(self, rosterSlotIdx, packedSlot):
        packedArgs = struct.pack('<B', rosterSlotIdx)
        packedArgs += packedSlot
        slot = self._roster.SLOT_TYPE(packed=packedSlot)
        roster = self._roster
        if slot.vehTypeCompDescr is None and slot.nationMask == 0 and slot.vehClassMask == 0:
            roster.slots.pop(rosterSlotIdx, None)
        else:
            neighbourSlotIdx = rosterSlotIdx ^ 1
            neighbourSlot = roster.slots.get(neighbourSlotIdx)
            if neighbourSlot and packedSlot == roster.DEFAULT_SLOT_PACK:
                LOG_DAN('_setRosterSlot: removing default slotIdx=%s' % rosterSlotIdx)
                roster.slots.pop(rosterSlotIdx, None)
            else:
                roster.slots[rosterSlotIdx] = slot
                if neighbourSlot and neighbourSlot.pack() == roster.DEFAULT_SLOT_PACK:
                    LOG_DAN('_setRosterSlot: removing default neighbour slotIdx=%s' % rosterSlotIdx)
                    roster.slots.pop(neighbourSlotIdx, None)
        roster.pack()
        self._dirty = 1
        self._appendOp(UNIT_OP.SET_SLOT, packedArgs)
        return

    def isEmpty(self):
        for playerID, playerInfo in self._players.iteritems():
            role = playerInfo.get('role', 0)
            if role & UNIT_ROLE.INVITED == 0:
                return False

        return True

    _HEADER = '<HHHHHHBi'
    _PLAYER_DATA = '<qiIHBHH'
    _PLAYER_VEHICLES = '<qiH'
    _SLOT_PLAYERS = '<Bq'
    _IDS = '<BBB'
    _VEHICLE_DICT_HEADER = '<Hq'
    _VEHICLE_DICT_ITEM = '<Hi'
    _HEADER_SIZE = struct.calcsize(_HEADER)
    _SLOT_PLAYERS_SIZE = struct.calcsize(_SLOT_PLAYERS)
    _PLAYER_DATA_SIZE = struct.calcsize(_PLAYER_DATA)
    _PLAYER_VEHICLES_SIZE = struct.calcsize(_PLAYER_VEHICLES)
    _IDS_SIZE = struct.calcsize(_IDS)
    _VEHICLE_DICT_HEADER_SIZE = struct.calcsize(_VEHICLE_DICT_HEADER)
    _VEHICLE_DICT_ITEM_SIZE = struct.calcsize(_VEHICLE_DICT_ITEM)

    def pack(self):
        packed = struct.pack(self._IDS, self._rosterTypeID, self._extrasHandlerID, self._prebattleTypeID)
        packed += self._roster.getPacked()
        members = self._members
        players = self._players
        vehs = self._vehicles
        extras = self._extras
        extrasStr = self._extrasHandler.pack(extras)
        args = (len(members),
         len(vehs),
         len(players),
         len(extrasStr),
         self._readyMask,
         self._state,
         self._closedSlotMask,
         self._modalTimestamp)
        packed += struct.pack(self._HEADER, *args)
        for playerID, veh in vehs.iteritems():
            packed += struct.pack(self._PLAYER_VEHICLES, playerID, veh['vehInvID'], veh['vehTypeCompDescr'])

        for slotIdx, member in members.iteritems():
            packed += struct.pack(self._SLOT_PLAYERS, slotIdx, member['playerID'])

        for playerID, playerData in players.iteritems():
            packed += struct.pack(self._PLAYER_DATA, playerID, playerData.get('accountID', 0), playerData.get('timeJoin', 0), playerData.get('role', 0), playerData.get('igrType', 0), playerData.get('rating', 0), playerData.get('peripheryID', 0))
            packed += packPascalString(playerData.get('nickName', ''))
            packed += packPascalString(playerData.get('clanAbbrev', ''))

        packed += extrasStr
        packed += packPascalString(self._strComment)
        self._packed = packed
        self._dirty = 0
        return packed

    def unpack(self, packed):
        self._initClean()
        self._rosterTypeID, self._extrasHandlerID, self._prebattleTypeID = struct.unpack_from(self._IDS, packed)
        RosterType = ROSTER_TYPE_TO_CLASS.get(self._rosterTypeID)
        self._roster = RosterType()
        self._extrasHandler = EXTRAS_HANDLER_TYPE_TO_HANDLER[self._extrasHandlerID](self)
        unpacking = packed[self._IDS_SIZE:]
        unpacking = self._roster.unpack(unpacking)
        slotCount = self.getMaxSlotCount()
        self._freeSlots = set(xrange(0, slotCount))
        memberCount, vehCount, playerCount, extrasLen, self._readyMask, self._state, self._closedSlotMask, self._modalTimestamp = struct.unpack_from(self._HEADER, unpacking)
        unpacking = unpacking[self._HEADER_SIZE:]
        for i in xrange(0, vehCount):
            playerID, vehInvID, vehTypeCompDescr = struct.unpack_from(self._PLAYER_VEHICLES, unpacking)
            self._setVehicle(playerID, vehTypeCompDescr, vehInvID)
            unpacking = unpacking[self._PLAYER_VEHICLES_SIZE:]

        for i in xrange(0, memberCount):
            slotIdx, playerID = struct.unpack_from(self._SLOT_PLAYERS, unpacking)
            self._setMember(playerID, slotIdx)
            unpacking = unpacking[self._SLOT_PLAYERS_SIZE:]

        sz = self._PLAYER_DATA_SIZE
        for i in xrange(0, playerCount):
            playerID, accountID, timeJoin, role, igrType, rating, peripheryID = struct.unpack_from(self._PLAYER_DATA, unpacking)
            nickName, lenNickBytes = unpackPascalString(unpacking, sz)
            clanAbbrev, lenClanBytes = unpackPascalString(unpacking, sz + lenNickBytes)
            unpacking = unpacking[sz + lenNickBytes + lenClanBytes:]
            self._addPlayer(playerID, accountID=accountID, timeJoin=timeJoin, role=role, rating=rating, nickName=nickName, clanAbbrev=clanAbbrev, peripheryID=peripheryID, igrType=igrType)

        self._extras = self._extrasHandler.unpack(unpacking[:extrasLen])
        unpacking = unpacking[extrasLen:]
        for slotIdx in range(0, 7):
            slotMask = 1 << slotIdx
            if self._closedSlotMask & slotMask:
                self._closeSlot(slotIdx)

        self._strComment, lenCommentBytes = unpackPascalString(unpacking, 0)
        unpacking = unpacking[lenCommentBytes:]
        lengthDiff = len(packed) - len(unpacking)
        self._packed = packed[:lengthDiff]
        self._packedOps = ''
        self._dirty = 0
        return unpacking

    def isDirty(self):
        return self._dirty

    def getCommanderDBID(self):
        return self._members[LEADER_SLOT]['playerID']

    def onUnitExtrasUpdate(self, updateStr):
        self._extrasHandler.onUnitExtrasUpdate(self._extras, updateStr)
        self.storeOp(UNIT_OP.EXTRAS_UPDATE, updateStr)
        for playerID, playerData in self._players.iteritems():
            if playerData and playerData.get('role', 0) & UNIT_ROLE.INVITED == 0:
                self._storeNotification(playerID, UNIT_NOTIFY_CMD.EXTRAS_UPDATED, [self, self._extras])

        self._dirty = 1

    def getPacked(self):
        if self._dirty:
            return self.pack()
        else:
            return self._packed

    def isReady(self):
        readyMask = self._readyMask
        return readyMask == self._fullReadyMask and readyMask

    def isLocked(self):
        return self._state & UNIT_STATE.LOCKED

    def isInviteOnly(self):
        return self._state & UNIT_STATE.INVITE_ONLY

    def isIdle(self):
        return self._state & UNIT_STATE.MODAL_STATES == 0

    def isDevMode(self):
        return self._state & UNIT_STATE.DEV_MODE

    def isInArena(self):
        return self._state & UNIT_STATE.IN_ARENA

    def isInPreArena(self):
        return self._state & UNIT_STATE.IN_PRE_ARENA

    def __repr__(self):
        repr = 'Unit(\n  _members len=%s {' % len(self._members)
        for slotIdx, member in self._members.iteritems():
            repr += '\n    [%d] %s' % (slotIdx, member)

        repr += '\n  },'
        repr += '\n  state=0x%02X, readyMask=0x%02X, fullReadyMask=0x%02X, closedSlotMask=0x%02X' % (self._state,
         self._readyMask,
         self._fullReadyMask,
         self._closedSlotMask)
        repr += '\n  state(names):%s' % _reprBitMaskFromDict(self._state, UNIT_STATE_NAMES)
        repr += '\n  modalTimestamp:%s' % self._modalTimestamp
        repr += '\n  _vehicles len=%s {' % len(self._vehicles)
        for playerID, veh in self._vehicles.iteritems():
            repr += '\n    [%d] %s' % (playerID, veh)

        repr += '\n  },'
        repr += '\n  _players len=%s {' % len(self._players)
        for playerID, playerData in self._players.iteritems():
            repr += '\n    [%d] %s role=%s' % (playerID, playerData, _reprBitMaskFromDict(playerData.get('role', 0), UNIT_ROLE_NAMES))

        repr += '\n  },'
        repr += '\n  _freeSlots=%r,' % self._freeSlots
        repr += '\n  _roster=%r' % self._roster
        repr += '\n _extras=%r' % self._extras
        repr += '\n  _strComment=%r' % self._strComment
        repr += '\n)'
        return repr

    def dump(self):
        repr = 'Unit(\n membs(%s)={' % len(self._members)
        for slotIdx, member in self._members.iteritems():
            repr += '%d:%s, ' % (slotIdx, member.get('playerID', 0))

        repr += '},'
        repr += '\n state=%02X, rdy=%02X, fullRdy=%02X, closed=%02X' % (self._state,
         self._readyMask,
         self._fullReadyMask,
         self._closedSlotMask)
        repr += ', stamp:%s, free=%r' % (self._modalTimestamp, list(self._freeSlots))
        repr += '\n vehs(%s)={' % len(self._vehicles)
        for playerID, veh in self._vehicles.iteritems():
            repr += '%d:%s, ' % (playerID, veh.get('vehTypeCompDescr', 0))

        repr += '},'
        repr += '\n plrs(%s)={' % len(self._players)
        for playerID, playerData in self._players.iteritems():
            repr += '%d:%r:%02X, ' % (playerID, playerData.get('nickName', ''), playerData.get('role', 0))

        repr += '},'
        repr += '\n roster=%r' % self._roster.getPacked()
        repr += '\n extras=%r' % self._extras
        repr += '\n)'
        return repr

    def setMemberReady(self, playerID, isReady=True):
        slotIdx = self._playerSlots.get(playerID)
        if slotIdx is None:
            return UNIT_ERROR.BAD_SLOT_IDX
        else:
            prevReadyMask = self._readyMask
            if isReady:
                veh = self._vehicles.get(playerID)
                if veh is None:
                    return UNIT_ERROR.VEHICLE_NOT_CHOSEN
                newReadyMask = prevReadyMask | 1 << slotIdx
            else:
                newReadyMask = prevReadyMask & ~(1 << slotIdx)
            if newReadyMask != prevReadyMask:
                self._readyMask = newReadyMask
                self.storeOp(UNIT_OP.READY_MASK, newReadyMask)
                self._dirty = 1
                self._storeNotification(playerID, UNIT_NOTIFY_CMD.SET_MEMBER_READY, [isReady])
            return OK

    def _setModalTimestamp(self, timestamp):
        self._modalTimestamp = timestamp
        self.storeOp(UNIT_OP.MODAL_TIMESTAMP, timestamp)
        self._dirty = 1

    def _setReadyMask(self, mask):
        self._readyMask = mask

    def _setUnitState(self, state):
        self._state = state

    def _closeSlot(self, slotIdx):
        self._closedSlotMask |= 1 << slotIdx
        self._freeSlots.discard(slotIdx)
        self._dirty = 1
        self.storeOp(UNIT_OP.CLOSE_SLOT, slotIdx)

    def getMaxSlotCount(self):
        if self._roster.slots:
            _max = max(self._roster.slots.iterkeys())
        else:
            _max = 0
        return _max / 2 + 1

    def getClosedSlotsCount(self):
        count = 0
        for i in xrange(self._roster.MAX_SLOTS):
            if self._closedSlotMask & 1 << i:
                count += 1

        return count

    def getPointsSum(self):
        sum = 0
        for slotIdx, member in self._members.iteritems():
            playerID = member.get('playerID', 0)
            veh = self._vehicles.get(playerID)
            if veh:
                sum += veh.get('vehLevel', 0)

        return sum

    def checkVehicleLevelsRange(self, minLvl, maxLvl):
        for slotIdx, member in self._members.iteritems():
            playerID = member.get('playerID', 0)
            veh = self._vehicles.get(playerID)
            if veh:
                lvl = veh.get('vehLevel', 0)
                if lvl < minLvl or maxLvl < lvl:
                    return False

        return True

    def getArtyCount(self):
        count = 0
        for slotIdx, member in self._members.iteritems():
            playerID = member.get('playerID', 0)
            veh = self._vehicles.get(playerID)
            if veh and veh['vehClassIdx'] == VEHICLE_CLASS_SPG:
                count += 1

        return count

    def hasInArenaMembers(self):
        for slotIdx, member in self._members.iteritems():
            playerID = member.get('playerID', 0)
            role = self.getAccountRole(playerID)
            if role & UNIT_ROLE.IN_ARENA:
                return True

        return False

    def getLegionaryCount(self):
        count = 0
        for playerID, slotIdx in self._playerSlots.iteritems():
            playerData = self._players[playerID]
            role = playerData.get('role', 0)
            if role & UNIT_ROLE.LEGIONARY:
                count += 1

        return count

    def getLegionaryMaxCount(self):
        return self._roster.getLegionariesMaxCount()

    def resetExtras(self):
        self._extras = self._extrasHandler.reset(self._extras)
        self.storeOp(UNIT_OP.EXTRAS_RESET)
        self._dirty = 1

    def _openSlot(self, slotIdx):
        self._closedSlotMask &= ~(1 << slotIdx)
        self._freeSlots.add(slotIdx)
        self._dirty = 1
        self.storeOp(UNIT_OP.OPEN_SLOT, slotIdx)

    def _reserveUnitSlot(self, unitSlotIdx):
        self._reservedSlots.add(unitSlotIdx)
        reservedRosterSlot = self._roster.SLOT_TYPE()
        reservedRosterSlot.vehTypeCompDescr = 0
        for slotIdx in (unitSlotIdx * 2, unitSlotIdx * 2 + 1):
            self._roster.slots[slotIdx] = reservedRosterSlot

    def setComment(self, strComment):
        self._strComment = strComment
        self.storeOp(UNIT_OP.SET_COMMENT, strComment)
        self._dirty = 1
        return OK

    def _appendCmdrOp(self, op, packedArgs):
        pass

    def _storeNotification(self, playerID, notifyCmd, argList=[]):
        pass

    def _unpackRosterSlot(self, packedOps):
        rosterSlotIdx = struct.unpack_from('<B', packedOps)[0]
        opLen = BaseUnitRosterSlot.getPackSize(packedOps[1]) + 1
        packedSlot = packedOps[1:opLen]
        self._setRosterSlot(rosterSlotIdx, packedSlot)
        return packedOps[opLen:]

    def _packVehicleDict(self, playerID, vehDict={}):
        packedArgs = struct.pack(self._VEHICLE_DICT_HEADER, len(vehDict), playerID)
        for vehTypeCompDescr, vehInvID in vehDict.iteritems():
            packedArgs += struct.pack(self._VEHICLE_DICT_ITEM, vehTypeCompDescr, vehInvID)

        self._appendCmdrOp(UNIT_OP.VEHICLE_DICT, packedArgs)

    def _packFullVehDictUpdates(self):
        for playerID, playerData in self._players.iteritems():
            if playerData and playerData.get('role', 0) & UNIT_ROLE.INVITED == 0:
                vehDict = playerData.get('vehDict')
                if vehDict:
                    self._packVehicleDict(playerID, vehDict)

    def _unpackVehicleDict(self, packedOps):
        vehCount, playerID = struct.unpack_from(self._VEHICLE_DICT_HEADER, packedOps)
        vehDict = {}
        opLen = self._VEHICLE_DICT_HEADER_SIZE
        for i in xrange(vehCount):
            vehTypeCompDescr, vehInvID = struct.unpack_from(self._VEHICLE_DICT_ITEM, packedOps, opLen)
            vehDict[vehTypeCompDescr] = vehInvID
            opLen += self._VEHICLE_DICT_ITEM_SIZE

        playerData = self._players.get(playerID)
        if playerData:
            playerData['vehDict'] = vehDict
        return packedOps[opLen:]

    def _unpackPlayer(self, packedOps):
        sz = self._PLAYER_DATA_SIZE
        playerID, accountID, timeJoin, role, igrType, rating, peripheryID = struct.unpack_from(self._PLAYER_DATA, packedOps)
        nickName, lenNickBytes = unpackPascalString(packedOps, sz)
        clanAbbrev, lenClanBytes = unpackPascalString(packedOps, sz + lenNickBytes)
        playerInfo = dict(accountID=accountID, role=role, timeJoin=timeJoin, rating=rating, nickName=nickName, clanAbbrev=clanAbbrev, peripheryID=peripheryID, igrType=igrType)
        self._addPlayer(playerID, **playerInfo)
        return packedOps[sz + lenNickBytes + lenClanBytes:]

    def _giveLeadership(self, newLeaderDBID):
        swapSlotIdx = self._playerSlots.get(newLeaderDBID)
        prevLeaderDBID = self._members[LEADER_SLOT]['playerID']
        self.setMemberReady(newLeaderDBID, False)
        if swapSlotIdx is not None:
            self._members[swapSlotIdx] = dict(playerID=prevLeaderDBID, slotIdx=swapSlotIdx)
            self._playerSlots[prevLeaderDBID] = swapSlotIdx
        else:
            self._playerSlots.pop(prevLeaderDBID)
        self._players[prevLeaderDBID]['role'] &= ~UNIT_ROLE.CREATOR
        self._members[LEADER_SLOT] = dict(playerID=newLeaderDBID, slotIdx=LEADER_SLOT)
        self._playerSlots[newLeaderDBID] = LEADER_SLOT
        self._players[newLeaderDBID]['role'] |= UNIT_ROLE.CREATOR
        self.storeOp(UNIT_OP.GIVE_LEADERSHIP, newLeaderDBID)
        return prevLeaderDBID

    def _changeSortieDivision(self, division):
        prevRosterTypeID = self._rosterTypeID
        prevRoster = self._roster
        LOG_SVAN_DEV('Previous roster type: {0} : {1}', prevRosterTypeID, prevRoster.__class__)
        newRosterTypeID = SORTIE_DIVISION_LEVEL_TO_FLAGS.get(division)
        if newRosterTypeID == prevRosterTypeID:
            LOG_SVAN_DEV('New division is an active. No changes are required.')
            return False
        self._rosterTypeID = newRosterTypeID
        RosterType = ROSTER_TYPE_TO_CLASS.get(newRosterTypeID)
        newRoster = RosterType()
        self._roster = newRoster
        LOG_SVAN_DEV('New roster type: {0} : {1}', self._rosterTypeID, self._roster.__class__)
        self.storeOp(UNIT_OP.CHANGE_DIVISION, division)
        return True

    def _getLeaderDBID(self):
        return self._members.get(LEADER_SLOT, {}).get('playerID', 0)

    def isRatedBattle(self):
        return bool(self._extras.get('isRatedBattle'))
