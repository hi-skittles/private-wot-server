# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/vehicles.py
# Compiled at: 2015-03-31 07:53:47
import types
from collections import namedtuple
from math import radians, cos, atan, pi
from functools import partial
import struct
import itertools
import ResMgr
from Math import Vector2, Vector3
from typing import Union, Tuple, Optional

import nations, items
from items import _xml
from debug_utils import *
from constants import IS_DEVELOPMENT, IS_CLIENT, IS_BOT, IS_CELLAPP, IS_BASEAPP, IS_WEB, ITEM_DEFS_PATH
from constants import DEFAULT_GUN_PITCH_LIMITS_TRANSITION, IGR_TYPE, IS_RENTALS_ENABLED
import BigWorld
if IS_CELLAPP or IS_CLIENT or IS_BOT:
    from ModelHitTester import ModelHitTester
if IS_CELLAPP or IS_CLIENT or IS_WEB:
    import material_kinds
    from material_kinds import EFFECT_MATERIALS
if IS_CLIENT:
    from helpers import i18n
    from helpers import EffectsList
    from VehicleEffects import ExhaustEffectsDescriptor, VehicleExhaustDescriptor
elif IS_WEB:
    from web_stubs import *
VEHICLE_CLASS_TAGS = frozenset(('lightTank',
 'mediumTank',
 'heavyTank',
 'SPG',
 'AT-SPG'))
VEHICLE_MODULE_TAGS_FOR_BALANCE_WEIGHT = frozenset(('vehicle',
 'gun',
 'turret',
 'engine',
 'chassis',
 'radio'))
VEHICLE_DEVICE_TYPE_NAMES = ('engine',
 'ammoBay',
 'fuelTank',
 'radio',
 'track',
 'gun',
 'turretRotator',
 'surveyingDevice')
VEHICLE_TANKMAN_TYPE_NAMES = ('commander',
 'driver',
 'radioman',
 'gunner',
 'loader')
OBLIGATORY_HB_TAGS = frozenset(('secret', 'cannot_be_sold', 'historical_battles'))
PREMIUM_IGR_TAGS = frozenset(('premiumIGR',))
NUM_OPTIONAL_DEVICE_SLOTS = 3
NUM_EQUIPMENT_SLOTS = 3
CAMOUFLAGE_KINDS = {
    'winter': 0,
    'summer': 1,
    'desert': 2
}

class HORN_COOLDOWN():
    WINDOW = 25.0
    CLIENT_WINDOW_EXPANSION = 5.0
    MAX_SIGNALS = 3


NUM_INSCRIPTION_COLORS = 16
KMH_TO_MS = 0.27778
HP_TO_WATTS = 735.5
g_list = None
g_cache = None
_VEHICLE_TYPE_XML_PATH = ITEM_DEFS_PATH + 'vehicles/'
_DEFAULT_SPECIFIC_FRICTION = 0.07 * 9.81
_DEFAULT_HEALTH_BURN_PER_SEC_LOSS_FRACTION = 0.0875
_CUSTOMIZATION_EPOCH = 1306886400
MaterialInfo = namedtuple('MaterialInfo', ['kind',
 'armor',
 'extra',
 'vehicleDamageFactor',
 'useArmorHomogenization',
 'useHitAngle',
 'useAntifragmentationLining',
 'mayRicochet',
 'collideOnceOnly',
 'damageKind',
 'chanceToHitByProjectile',
 'chanceToHitByExplosion',
 'continueTraceIfNoHit'])
_defMaterialInfo = MaterialInfo(0, 0, None, 0.0, False, False, False, False, False, 0, 0.0, 0.0, False)
EmblemSlot = namedtuple('EmblemSlot', ['rayStart',
 'rayEnd',
 'rayUp',
 'size',
 'hideIfDamaged',
 'type',
 'isMirrored',
 'emblemId'])

def init(preloadEverything, pricesToCollect):
    # type: (bool, dict or None) -> None
    """Initialize vehicle caches and optional price collection.

    :param preloadEverything: When ``True`` all resources are loaded
        immediately.
    :param pricesToCollect: Destination dictionary for price data or
        ``None`` to skip collecting prices.
    :return: ``None``
    """
    global g_list
    global g_cache
    global _g_prices
    if IS_CLIENT or IS_CELLAPP:
        import vehicle_extras
    _g_prices = pricesToCollect
    if pricesToCollect is not None:
        pricesToCollect['itemPrices'] = {}
        pricesToCollect['vehiclesRentPrices'] = {}
        pricesToCollect['notInShopItems'] = set()
        pricesToCollect['vehiclesNotToBuy'] = set()
        pricesToCollect['vehiclesToSellForGold'] = set()
        pricesToCollect['vehicleSellPriceFactors'] = {}
        pricesToCollect['vehicleCamouflagePriceFactors'] = {}
        pricesToCollect['vehicleHornPriceFactors'] = {}
        pricesToCollect['hornPrices'] = {}
        pricesToCollect['camouflagePriceFactors'] = [ {} for x in nations.NAMES ]
        pricesToCollect['notInShopCamouflages'] = [ set() for x in nations.NAMES ]
        pricesToCollect['inscriptionGroupPriceFactors'] = [ {} for x in nations.NAMES ]
        pricesToCollect['notInShopInscriptionGroups'] = [ set() for x in nations.NAMES ]
        pricesToCollect['playerEmblemGroupPriceFactors'] = {}
        pricesToCollect['notInShopPlayerEmblemGroups'] = set()
    g_list = VehicleList()
    g_cache = Cache()
    if preloadEverything:
        g_cache.optionalDevices()
        g_cache.equipments()
        g_cache.horns()
        g_cache.playerEmblems()
        for nationID in xrange(len(nations.NAMES)):
            g_cache.customization(nationID)
            g_cache.shells(nationID)
            for vehicleTypeID in g_list.getList(nationID).iterkeys():
                g_cache.vehicle(nationID, vehicleTypeID)

        _g_prices = None
    return


def reload():
    # type: () -> None
    """Reload vehicle definitions and reinitialize caches. Client only."""
    import vehicle_extras
    vehicle_extras.reload()
    from sys import modules
    import __builtin__
    __builtin__.reload(modules[reload.__module__])
    init(True, {})


class VehicleDescr(object):

    def __init__(self, compactDescr=None, typeID=None, typeName=None):
        # type: (str or None, tuple or None, str or None) -> None
        """Create a vehicle description from identifiers or compact descriptor.

        Exactly one of ``compactDescr``, ``typeID`` or ``typeName`` should be
        provided.  When ``compactDescr`` is ``None`` the method builds one using
        the cache and initial equipment of the vehicle type.
        """
        if compactDescr is None:
            if typeID is not None:
                nationID, vehicleTypeID = typeID
            else:
                assert typeName is not None
                nationID, vehicleTypeID = g_list.getIDsByName(typeName)
            type = g_cache.vehicle(nationID, vehicleTypeID)
            turretDescr = type.turrets[0][0]
            header = items.ITEM_TYPES.vehicle + (nationID << 4)
            compactDescr = struct.pack('<2B6HB', header, vehicleTypeID, type.chassis[0]['id'][1], type.engines[0]['id'][1], type.fuelTanks[0]['id'][1], type.radios[0]['id'][1], turretDescr['id'][1], turretDescr['guns'][0]['id'][1], 0)
        self.__initFromCompactDescr(compactDescr)
        return

    def __set_activeTurretPos(self, turretPosition):
        self.turret, self.gun = self.turrets[turretPosition]
        self.__activeTurretPos = turretPosition
        self.activeGunShotIndex = 0

    activeTurretPosition = property(lambda self: self.__activeTurretPos, __set_activeTurretPos)

    def __set_activeGunShotIndex(self, shotIndex):
        self.shot = self.gun['shots'][shotIndex]
        self.__activeGunShotIdx = shotIndex

    activeGunShotIndex = property(lambda self: self.__activeGunShotIdx, __set_activeGunShotIndex)

    def __set_hornID(self, id):
        if id is not None:
            descr = g_cache.horns()[id]
            if not self.type.tags.intersection(descr['vehicleTags']):
                raise Exception, 'horn is incompatible with vehicle'
        self.__hornID = id
        return

    hornID = property(lambda self: self.__hornID, __set_hornID)

    def __get_boundingRadius(self):
        radius = getattr(self, '_VehicleDescr__boundingRadius', None)
        if radius is None:
            chassisDescr = self.chassis
            hullDescr = self.hull
            hullOnChassisOffsetZ = chassisDescr['hullPosition'].z
            turretOnHullOffsetZ = hullDescr['turretPositions'][0].z
            gunOnTurretOffsetZ = self.turret['gunPosition'].z
            chassisBbox = chassisDescr['hitTester'].bbox
            hullBbox = hullDescr['hitTester'].bbox
            bboxMin = Vector2(min(chassisBbox[0].x, hullBbox[0].x), min(chassisBbox[0].z, hullBbox[0].z + hullOnChassisOffsetZ))
            bboxMax = Vector2(max(chassisBbox[1].x, hullBbox[1].x), max(chassisBbox[1].z, hullBbox[1].z + hullOnChassisOffsetZ))
            gunOnTurretMaxZ = gunOnTurretOffsetZ + self.gun['hitTester'].bbox[1].z
            radius = max(bboxMin.length, bboxMax.length, abs(hullOnChassisOffsetZ + turretOnHullOffsetZ + gunOnTurretMaxZ), abs(hullOnChassisOffsetZ + turretOnHullOffsetZ - gunOnTurretMaxZ))
            self.__boundingRadius = radius
        return radius

    boundingRadius = property(__get_boundingRadius)

    def setCamouflage(self, position, camouflageID, startTime, durationDays):
        # type: (int, int or None, int, int) -> None
        """Apply a camouflage to the vehicle.

        :param position: Slot index or camouflage kind.
        :param camouflageID: Camouflage identifier or ``None`` to remove.
        :param startTime: Activation timestamp in seconds.
        :param durationDays: Duration of the camouflage in days.
        """
        p = self.camouflages
        if camouflageID is None:
            startTime = _CUSTOMIZATION_EPOCH
            durationDays = 0
            p[position]
        else:
            descr = g_cache.customization(self.type.customizationNationID)['camouflages'][camouflageID]
            if position is None:
                position = descr['kind']
            elif position != descr['kind']:
                raise Exception, 'wrong camouflage kind'
            cd = self.type.compactDescr
            if cd in descr['deny']:
                raise Exception, 'camouflage is incompatible with vehicle'
            if descr['allow'] and cd not in descr['allow']:
                raise Exception, 'camouflage is incompatible with vehicle'
            startTime = int(startTime / 60) * 60
            if startTime < _CUSTOMIZATION_EPOCH:
                raise Exception, 'wrong camouflage start time'
            durationDays = int(durationDays)
            if not 0 <= durationDays <= 255:
                raise Exception, 'wrong camouflage duration'
        self.camouflages = p[:position] + ((camouflageID, startTime, durationDays),) + p[position + 1:]
        return

    def setPlayerEmblem(self, position, emblemID, startTime, durationDays):
        # type: (int, int or None, int, int) -> None
        """Set or clear a player emblem on the vehicle.

        :param position: Emblem slot index.
        :param emblemID: Emblem identifier or ``None`` to remove.
        :param startTime: Activation start time (minutes aligned).
        :param durationDays: Number of days the emblem remains active.
        """
        p = self.playerEmblems
        p[position]
        defEmblemID = self.type.defaultPlayerEmblemID
        if emblemID is None or emblemID == defEmblemID:
            emblemID = defEmblemID
            startTime = _CUSTOMIZATION_EPOCH
            durationDays = 0
        else:
            groups, emblems, names = g_cache.playerEmblems()
            emblem = emblems[emblemID]
            groupName = emblem[0]
            group = groups[groupName]
            nations = group[3]
            if nations is not None and self.type.customizationNationID not in nations:
                raise Exception, 'emblem nation mismatch'
            allow, deny = group[4:6]
            cd = self.type.compactDescr
            if cd in deny:
                raise Exception, 'emblem is incompatible with vehicle'
            if allow and cd not in allow:
                raise Exception, 'emblem is incompatible with vehicle'
            startTime = int(startTime / 60) * 60
            if startTime < _CUSTOMIZATION_EPOCH:
                raise Exception, 'wrong emblem start time'
            durationDays = int(durationDays)
            if not 0 <= durationDays <= 255:
                raise Exception, 'wrong emblem duration'
        self.playerEmblems = p[:position] + ((emblemID, startTime, durationDays),) + p[position + 1:]
        return

    def setPlayerInscription(self, position, inscriptionID, startTime, durationDays, color):
        # type: (int, int or None, int, int, int) -> None
        """Apply or remove a player inscription.

        :param position: Inscription slot index.
        :param inscriptionID: Inscription identifier or ``None`` to remove.
        :param startTime: Activation start time.
        :param durationDays: Number of days the inscription remains.
        :param color: Colour index used for the inscription.
        """
        p = self.playerInscriptions
        p[position]
        if inscriptionID is None:
            startTime = _CUSTOMIZATION_EPOCH
            durationDays = 0
            color = 0
        else:
            customization = g_cache.customization(self.type.customizationNationID)
            groupName = customization['inscriptions'][inscriptionID][0]
            customization['inscriptionColors'][color]
            allow, deny = customization['inscriptionGroups'][groupName][3:5]
            cd = self.type.compactDescr
            if cd in deny:
                raise Exception, 'inscription is incompatible with vehicle'
            if allow and cd not in allow:
                raise Exception, 'inscription is incompatible with vehicle'
            startTime = int(startTime / 60) * 60
            if startTime < _CUSTOMIZATION_EPOCH:
                raise Exception, 'wrong inscription start time'
            durationDays = int(durationDays)
            if not 0 <= durationDays <= 255:
                raise Exception, 'wrong inscription duration'
        self.playerInscriptions = p[:position] + ((inscriptionID,
          startTime,
          durationDays,
          color),) + p[position + 1:]
        return

    def getComponentsByType(self, itemTypeName, positionIndex=0):
        # type: (str, int) -> tuple
        """Return installed component and available list for given type."""
        if itemTypeName == 'vehicleChassis':
            return (self.chassis, self.type.chassis)
        if itemTypeName == 'vehicleEngine':
            return (self.engine, self.type.engines)
        if itemTypeName == 'vehicleRadio':
            return (self.radio, self.type.radios)
        if itemTypeName == 'vehicleFuelTank':
            return (self.fuelTank, self.type.fuelTanks)
        if itemTypeName == 'vehicleTurret':
            return (self.turrets[positionIndex][0], self.type.turrets[positionIndex])
        if itemTypeName == 'vehicleGun':
            turretDescr, gunDescr = self.turrets[positionIndex]
            return (gunDescr, turretDescr['guns'])
        assert False

    def mayInstallTurret(self, turretCompactDescr, gunCompactDescr, positionIndex=0):
        # type: (int, int, int) -> Union[None, Tuple[bool, str], Tuple[bool, None]]
        """Check turret and gun compatibility with the vehicle.

        :return: Tuple ``(is_ok, reason)`` where ``reason`` is ``None`` when
            installation is possible.
        """
        selfType = self.type
        selfTurrets = self.turrets
        itemTypeID, nationID, turretID = parseIntCompactDescr(turretCompactDescr)
        if items.ITEM_TYPE_NAMES[itemTypeID] != 'vehicleTurret':
            return (False, 'wrong item type')
        elif nationID != selfType.id[0]:
            return (False, 'wrong nation')
        else:
            if gunCompactDescr == 0:
                gunID = selfTurrets[positionIndex][1]['id'][1]
            else:
                itemTypeID, nationID, gunID = parseIntCompactDescr(gunCompactDescr)
                if items.ITEM_TYPE_NAMES[itemTypeID] != 'vehicleGun':
                    return (False, 'wrong item type')
                if nationID != selfType.id[0]:
                    return (False, 'wrong nation')
            newTurretDescr = _findDescrByID(selfType.turrets[positionIndex], turretID)
            if newTurretDescr is None:
                return (False, 'not for this vehicle type')
            newGunDescr = _findDescrByID(newTurretDescr['guns'], gunID)
            if newGunDescr is None:
                if gunCompactDescr not in selfType.installableComponents:
                    return (False, 'not for this vehicle type')
                return (False, 'not for current vehicle')
            setter = partial(selfTurrets.__setitem__, positionIndex, (newTurretDescr, newGunDescr))
            restorer = partial(selfTurrets.__setitem__, positionIndex, selfTurrets[positionIndex])
            if len(selfType.hulls) > 1:
                turrets = list(selfTurrets)
                turrets[positionIndex] = (newTurretDescr, newGunDescr)
                hullDescr = self.__selectBestHull(turrets, self.chassis)
                if hullDescr is not self.hull:
                    setter = partial(self.__setHullAndCall, hullDescr, setter)
                    restorer = partial(self.__setHullAndCall, self.hull, restorer)
            try:
                prevWeight = self.__computeWeight()
                setter()
                if self.__haveIncompatibleOptionalDevices():
                    return (False, 'not for current vehicle')
                if not _isWeightAllowedToChange(self.__computeWeight(), prevWeight):
                    return (False, 'too heavy')
            finally:
                restorer()

            return (True, None)

    def installTurret(self, turretCompactDescr, gunCompactDescr, positionIndex=0):
        # type: (int, int, int) -> list
        """Install a new turret (and optionally gun) on the vehicle.

        :return: List of compact descriptors of removed components.
        """
        turretID = parseIntCompactDescr(turretCompactDescr)[2]
        if gunCompactDescr == 0:
            gunID = self.turrets[positionIndex][1]['id'][1]
        else:
            gunID = parseIntCompactDescr(gunCompactDescr)[2]
        prevTurretDescr, prevGunDescr = self.turrets[positionIndex]
        newTurretDescr = _descrByID(self.type.turrets[positionIndex], turretID)
        newGunDescr = _descrByID(newTurretDescr['guns'], gunID)
        self.turrets[positionIndex] = (newTurretDescr, newGunDescr)
        if len(self.type.hulls) > 1:
            self.hull = self.__selectBestHull(self.turrets, self.chassis)
        self.__updateAttributes()
        if self.__activeTurretPos == positionIndex:
            self.activeTurretPosition = positionIndex
        removed = [prevTurretDescr['compactDescr']]
        if gunCompactDescr != 0:
            removed.append(prevGunDescr['compactDescr'])
        return removed

    def mayInstallComponent(self, compactDescr, positionIndex=0):
        # type: (int, int) -> Union[None, Tuple[bool, str], Tuple[bool, None]]
        """Check whether a component can be installed.

        :return: tuple ``(is_ok, reason)`` similar to :meth:`mayInstallTurret`.
        """
        itemTypeID, nationID, compID = parseIntCompactDescr(compactDescr)
        itemTypeName = items.ITEM_TYPE_NAMES[itemTypeID]
        selfType = self.type
        if nationID != selfType.id[0]:
            return (False, 'wrong nation')
        else:
            if itemTypeName == 'vehicleGun':
                hullDescr = self.hull
                turretDescr = self.turrets[positionIndex][0]
                newDescr = _findDescrByID(turretDescr['guns'], compID)
                if newDescr is None and positionIndex in hullDescr['fakeTurrets']['lobby']:
                    newDescr, turretDescr, hullDescr = self.__selectTurretForGun(compID, positionIndex)
                setter = partial(self.turrets.__setitem__, positionIndex, (turretDescr, newDescr))
                restorer = partial(self.turrets.__setitem__, positionIndex, self.turrets[positionIndex])
                if hullDescr is not self.hull:
                    setter = partial(self.__setHullAndCall, hullDescr, setter)
                    restorer = partial(self.__setHullAndCall, self.hull, restorer)
            elif itemTypeName == 'vehicleChassis':
                newDescr = _findDescrByID(selfType.chassis, compID)
                setter = partial(setattr, self, 'chassis', newDescr)
                restorer = partial(setattr, self, 'chassis', self.chassis)
                if len(selfType.hulls) > 1:
                    hullDescr = self.__selectBestHull(self.turrets, newDescr)
                    if hullDescr is not self.hull:
                        setter = partial(self.__setHullAndCall, hullDescr, setter)
                        restorer = partial(self.__setHullAndCall, self.hull, restorer)
            elif itemTypeName == 'vehicleEngine':
                newDescr = _findDescrByID(selfType.engines, compID)
                setter = partial(setattr, self, 'engine', newDescr)
                restorer = partial(setattr, self, 'engine', self.engine)
            elif itemTypeName == 'vehicleRadio':
                newDescr = _findDescrByID(selfType.radios, compID)
                setter = partial(setattr, self, 'radio', newDescr)
                restorer = partial(setattr, self, 'radio', self.radio)
            elif itemTypeName == 'vehicleFuelTank':
                newDescr = _findDescrByID(selfType.fuelTanks, compID)
                setter = partial(setattr, self, 'fuelTank', newDescr)
                restorer = partial(setattr, self, 'fuelTank', self.fuelTank)
            else:
                return (False, 'wrong item type')
            if newDescr is None:
                if compactDescr not in selfType.installableComponents:
                    return (False, 'not for this vehicle type')
                return (False, 'not for current vehicle')
            try:
                prevWeight = self.__computeWeight()
                setter()
                if self.__haveIncompatibleOptionalDevices():
                    return (False, 'not for current vehicle')
                if not _isWeightAllowedToChange(self.__computeWeight(), prevWeight):
                    return (False, 'too heavy')
            finally:
                restorer()

            return (True, None)

    def installComponent(self, compactDescr, positionIndex=0):
        # type: (int, int) -> tuple
        """Install the specified component and return the removed one."""
        itemTypeID, nationID, compID = parseIntCompactDescr(compactDescr)
        itemTypeName = items.ITEM_TYPE_NAMES[itemTypeID]
        if nationID != self.type.id[0]:
            raise Exception, 'incompatible nation of component'
        if itemTypeName == 'vehicleGun':
            return self.__installGun(compID, positionIndex)
        if itemTypeName == 'vehicleChassis':
            attrName = 'chassis'
            compList = self.type.chassis
        elif itemTypeName == 'vehicleEngine':
            attrName = 'engine'
            compList = self.type.engines
        elif itemTypeName == 'vehicleRadio':
            attrName = 'radio'
            compList = self.type.radios
        elif itemTypeName == 'vehicleFuelTank':
            attrName = 'fuelTank'
            compList = self.type.fuelTanks
        else:
            assert False
        prevDescr = getattr(self, attrName)
        newDescr = _descrByID(compList, compID)
        setattr(self, attrName, newDescr)
        if attrName == 'chassis' and len(self.type.hulls) > 1:
            self.hull = self.__selectBestHull(self.turrets, self.chassis)
        self.__updateAttributes()
        return (prevDescr['compactDescr'],)

    def mayInstallOptionalDevice(self, compactDescr, slotIdx):
        # type: (int, int) -> Union[None, Tuple[bool, str], Tuple[bool, None]]
        """Check whether an optional device can be installed in the slot."""
        itemTypeID, _, deviceID = parseIntCompactDescr(compactDescr)
        if items.ITEM_TYPE_NAMES[itemTypeID] != 'optionalDevice':
            return (False, 'wrong item type')
        else:
            device = g_cache.optionalDevices()[deviceID]
            prevDevices = self.optionalDevices
            if device in prevDevices:
                return (False, 'already installed')
            devices = list(prevDevices)
            self.optionalDevices = devices
            try:
                prevWeight = self.__computeWeight()
                devices[slotIdx] = None
                res = device.checkCompatibilityWithVehicle(self)
                if not res[0]:
                    return res
                devices[slotIdx] = device
                if self.__haveIncompatibleOptionalDevices():
                    return (False, 'not for current vehicle')
                if not _isWeightAllowedToChange(self.__computeWeight(), prevWeight):
                    return (False, 'too heavy')
            finally:
                self.optionalDevices = prevDevices

            return (True, None)

    def installOptionalDevice(self, compactDescr, slotIdx):
        # type: (int, int) -> tuple
        """Install an optional device and return removed or destroyed device."""
        device = g_cache.optionalDevices()[parseIntCompactDescr(compactDescr)[2]]
        devices = self.optionalDevices
        prevDevice = devices[slotIdx]
        devices[slotIdx] = device
        self.__updateAttributes()
        if prevDevice is None:
            return ((), ())
        else:
            return ((prevDevice.compactDescr,), ()) if prevDevice['removable'] else ((), (prevDevice.compactDescr,))

    def mayRemoveOptionalDevice(self, slotIdx):
        # type: (int) -> Optional[Tuple[bool, Union[None, str]]]
        """Check if optional device removal is allowed."""
        prevDevices = self.optionalDevices
        devices = list(prevDevices)
        self.optionalDevices = devices
        try:
            prevWeight = self.__computeWeight()
            devices[slotIdx] = None
            if self.__haveIncompatibleOptionalDevices():
                return (False, 'not for current vehicle')
            if not _isWeightAllowedToChange(self.__computeWeight(), prevWeight):
                return (False, 'too heavy')
        finally:
            self.optionalDevices = prevDevices

        return (True, None)

    def removeOptionalDevice(self, slotIdx):
        # type: (int) -> tuple
        """Remove an optional device from the vehicle."""
        device = self.optionalDevices[slotIdx]
        self.optionalDevices[slotIdx] = None
        self.__updateAttributes()
        if device is None:
            return ((), ())
        else:
            return ((device.compactDescr,), ()) if device['removable'] else ((), (device.compactDescr,))

    def makeCompactDescr(self):
        # type: () -> str
        """Serialize current vehicle state into compact descriptor."""
        type = self.type
        pack = struct.pack
        components = pack('<4H', self.chassis['id'][1], self.engine['id'][1], self.fuelTank['id'][1], self.radio['id'][1])
        for n in xrange(len(type.turrets)):
            turretDescr, gunDescr = self.turrets[n]
            components += pack('<2H', turretDescr['id'][1], gunDescr['id'][1])

        optionalDevices = ''
        optionalDeviceSlots = 0
        assert len(self.optionalDevices) == NUM_OPTIONAL_DEVICE_SLOTS
        for device in self.optionalDevices:
            optionalDeviceSlots <<= 1
            if device is not None:
                optionalDevices = pack('<H', device.id[1]) + optionalDevices
                optionalDeviceSlots |= 1

        emblemPositions = 0
        emblems = ''
        for idx, item in enumerate(self.playerEmblems):
            if item[0] is not None and item[0] != type.defaultPlayerEmblemID:
                emblemPositions |= 1 << idx
                emblems += _packIDAndDuration(*item)

        inscriptions = ''
        for idx, item in enumerate(self.playerInscriptions):
            if item[0] is not None:
                emblemPositions |= 1 << idx + 4
                inscriptions += _packIDAndDuration(item[0], item[1], item[2]) + chr(item[3])

        camouflages = ''
        for item in self.camouflages:
            if item[0] is not None:
                camouflages += _packIDAndDuration(*item)

        return _combineVehicleCompactDescr(type, components, optionalDeviceSlots, optionalDevices, emblemPositions, emblems, inscriptions, camouflages, self.__hornID)

    def getCost(self, itemPrices):
        # type: (dict) -> tuple
        """Calculate total purchase cost of the vehicle."""
        type = self.type
        cost = itemPrices[type.compactDescr]
        for idx in xrange(len(self.turrets)):
            turretDescr, gunDescr = self.turrets[idx]
            cost = _summPriceDiff(cost, itemPrices[turretDescr['compactDescr']], itemPrices[type.turrets[idx][0]['compactDescr']])
            cost = _summPriceDiff(cost, itemPrices[gunDescr['compactDescr']], itemPrices[turretDescr['guns'][0]['compactDescr']])

        cost = _summPriceDiff(cost, itemPrices[self.chassis['compactDescr']], itemPrices[type.chassis[0]['compactDescr']])
        cost = _summPriceDiff(cost, itemPrices[self.engine['compactDescr']], itemPrices[type.engines[0]['compactDescr']])
        cost = _summPriceDiff(cost, itemPrices[self.fuelTank['compactDescr']], itemPrices[type.fuelTanks[0]['compactDescr']])
        cost = _summPriceDiff(cost, itemPrices[self.radio['compactDescr']], itemPrices[type.radios[0]['compactDescr']])
        for device in self.optionalDevices:
            if device is not None:
                cost = _summPriceDiff(cost, itemPrices[device.compactDescr], (0, 0))

        return cost

    def getMaxRepairCost(self):
        # type: () -> float
        """Return maximal possible repair cost for the vehicle."""
        type = self.type
        cost = self.maxHealth * type.repairCost
        for turretDescr, gunDescr in self.turrets:
            cost += _getMaxCompRepairCost(gunDescr) + _getMaxCompRepairCost(turretDescr['turretRotatorHealth']) + _getMaxCompRepairCost(turretDescr['surveyingDeviceHealth'])

        cost += _getMaxCompRepairCost(self.hull['ammoBayHealth']) + _getMaxCompRepairCost(self.chassis) * 2 + _getMaxCompRepairCost(self.engine) + _getMaxCompRepairCost(self.fuelTank) + _getMaxCompRepairCost(self.radio)
        return cost

    def getDevices(self):
        # type: () -> tuple
        """Return tuples with default, installed and optional device CDs."""
        defComps = []
        instComps = []
        type = self.type
        instComps.append(self.chassis['compactDescr'])
        defComps.append(type.chassis[0]['compactDescr'])
        instComps.append(self.engine['compactDescr'])
        defComps.append(type.engines[0]['compactDescr'])
        instComps.append(self.fuelTank['compactDescr'])
        defComps.append(type.fuelTanks[0]['compactDescr'])
        instComps.append(self.radio['compactDescr'])
        defComps.append(type.radios[0]['compactDescr'])
        for (turretDescr, gunDescr), turrets in zip(self.turrets, type.turrets):
            instComps.append(turretDescr['compactDescr'])
            defComps.append(turrets[0]['compactDescr'])
            instComps.append(gunDescr['compactDescr'])
            defComps.append(turretDescr['guns'][0]['compactDescr'])

        optDevices = []
        for device in self.optionalDevices:
            if device is not None:
                optDevices.append(device.compactDescr)

        return (defComps, instComps, optDevices)

    def getHitTesters(self):
        # type: () -> list
        """Return hit tester objects for all vehicle parts."""
        hitTesters = [self.chassis['hitTester'], self.hull['hitTester']]
        for turretDescr, gunDescr in self.turrets:
            hitTesters.append(turretDescr['hitTester'])
            hitTesters.append(gunDescr['hitTester'])

        return hitTesters

    def prerequisites(self):
        # type: () -> list
        """Return resource prerequisites required by this vehicle."""
        prereqs = set()
        for effGroup in self.type.effects.values():
            for keyPoints, effects, readyPrereqs in effGroup:
                if not readyPrereqs:
                    prereqs.update(effects.prerequisites())

        if self.chassis['effects'] is not None:
            if self.chassis['effects']['dust'] is not None:
                effGroup, readyPrereqs = self.chassis['effects']['dust']
                if not readyPrereqs:
                    prereqs.update(self.__getChassisEffectNames(effGroup))
            if self.chassis['effects']['mud'] is not None:
                effGroup, readyPrereqs = self.chassis['effects']['mud']
                if not readyPrereqs:
                    prereqs.update(self.__getChassisEffectNames(effGroup))
        for turretDescr, gunDescr in self.turrets:
            detachmentEff = turretDescr['turretDetachmentEffects']
            detachmentEff = itertools.chain((detachmentEff['flight'], detachmentEff['flamingOnGround']), detachmentEff['collision'].itervalues())
            for stages, effects, readyPrereqs in detachmentEff:
                if not readyPrereqs:
                    prereqs.update(effects.prerequisites())

            if gunDescr['effects'] is not None:
                keyPoints, effects, readyPrereqs = gunDescr['effects']
                if not readyPrereqs:
                    prereqs.update(effects.prerequisites())
            for shotDescr in gunDescr['shots']:
                effectsDescr = g_cache.shotEffects[shotDescr['shell']['effectsIndex']]
                if not effectsDescr['prereqs']:
                    projectileModel, projectileOwnShotModel, effects = effectsDescr['projectile']
                    prereqs.add(projectileModel)
                    prereqs.add(projectileOwnShotModel)
                    prereqs.update(effects.prerequisites())
                    for materialName in EFFECT_MATERIALS:
                        prereqs.update(effectsDescr[materialName + 'Hit'][1].prerequisites())

                    prereqs.update(effectsDescr['shallowWaterHit'][1].prerequisites())
                    prereqs.update(effectsDescr['deepWaterHit'][1].prerequisites())
                    prereqs.update(effectsDescr['armorResisted'][1].prerequisites())
                    prereqs.update(effectsDescr['armorBasicRicochet'][1].prerequisites())
                    prereqs.update(effectsDescr['armorRicochet'][1].prerequisites())
                    prereqs.update(effectsDescr['armorHit'][1].prerequisites())
                    prereqs.update(effectsDescr['armorCriticalHit'][1].prerequisites())

        if self.type._prereqs is None:
            prereqs.update(self.hull['exhaust'].prerequisites())
            for extra in self.extras:
                prereqs.update(extra.prerequisites())

        return list(prereqs)

    def keepPrereqs(self, prereqs):
        # type: (list) -> None
        """Filter and cache prerequisite resources needed by the vehicle."""
        if not prereqs:
            return
        else:
            for effGroup in self.type.effects.values():
                for keyPoints, effects, readyPrereqs in effGroup:
                    if not readyPrereqs:
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effects.prerequisites()))

            if self.chassis['effects'] is not None:
                if self.chassis['effects']['dust'] is not None:
                    effGroup, readyPrereqs = self.chassis['effects']['dust']
                    if not readyPrereqs:
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, self.__getChassisEffectNames(effGroup)))
                if self.chassis['effects']['mud'] is not None:
                    effGroup, readyPrereqs = self.chassis['effects']['mud']
                    if not readyPrereqs:
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, self.__getChassisEffectNames(effGroup)))
            for turretDescr, gunDescr in self.turrets:
                detachmentEff = turretDescr['turretDetachmentEffects']
                detachmentEff = itertools.chain((detachmentEff['flight'], detachmentEff['flamingOnGround']), detachmentEff['collision'].itervalues())
                for stages, effects, readyPrereqs in detachmentEff:
                    if not readyPrereqs:
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effects.prerequisites()))

                keyPoints, effects, readyPrereqs = gunDescr['effects']
                if not readyPrereqs:
                    readyPrereqs.update(_extractNeededPrereqs(prereqs, effects.prerequisites()))
                for shotDescr in gunDescr['shots']:
                    effectsDescr = g_cache.shotEffects[shotDescr['shell']['effectsIndex']]
                    readyPrereqs = effectsDescr['prereqs']
                    if not readyPrereqs:
                        projectileModel, projectileOwnShotModel, effects = effectsDescr['projectile']
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, (projectileModel, projectileOwnShotModel)))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effects.prerequisites()))
                        for materialName in EFFECT_MATERIALS:
                            readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr[materialName + 'Hit'][1].prerequisites()))

                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['shallowWaterHit'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['deepWaterHit'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorResisted'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorBasicRicochet'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorRicochet'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorHit'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorCriticalHit'][1].prerequisites()))

            if self.type._prereqs is None:
                resourceNames = list(self.hull['exhaust'].prerequisites())
                for extra in self.extras:
                    resourceNames += extra.prerequisites()

                self.type._prereqs = _extractNeededPrereqs(prereqs, resourceNames)
            return

    def __getChassisEffectNames(self, effectGroup):
        ret = []
        for v in effectGroup.values():
            if isinstance(v, list):
                for s in v:
                    ret.append(s)

            ret.append(v)

        return ret

    def __installGun(self, gunID, turretPositionIdx):
        turretDescr, prevGunDescr = self.turrets[turretPositionIdx]
        newGunDescr = _findDescrByID(turretDescr['guns'], gunID)
        hullDescr = self.hull
        if newGunDescr is None and turretPositionIdx in self.hull['fakeTurrets']['lobby']:
            newGunDescr, turretDescr, hullDescr = self.__selectTurretForGun(gunID, turretPositionIdx)
        if newGunDescr is None:
            raise KeyError
        self.turrets[turretPositionIdx] = (turretDescr, newGunDescr)
        self.hull = hullDescr
        self.__updateAttributes()
        if self.__activeTurretPos == turretPositionIdx:
            self.activeTurretPosition = turretPositionIdx
        return (prevGunDescr['compactDescr'],)

    def __selectBestHull(self, turrets, chassis):
        turretIDs = [ descr[0]['id'][1] for descr in turrets ]
        chassisID = chassis['id'][1]
        hulls = self.type.hulls
        bestHull = hulls[0]
        bestMatchWeight = 0
        for hull in hulls[1:]:
            match = hull['variantMatch']
            matchWeight = 0
            if match[0] is not None:
                if match[0] != chassisID:
                    continue
                matchWeight = 100
            for turretID, turretToMatchID in zip(turretIDs, match[1:]):
                if turretToMatchID is None:
                    continue
                if turretID == turretToMatchID:
                    matchWeight += 1
                matchWeight = -1
                break

            if bestMatchWeight < matchWeight:
                bestMatchWeight = matchWeight
                bestHull = hull

        return bestHull

    def __selectTurretForGun(self, gunID, turretPositionIdx):
        hullDescr = self.hull
        for turretDescr in self.type.turrets[turretPositionIdx]:
            gunDescr = _findDescrByID(turretDescr['guns'], gunID)
            if gunDescr is not None:
                if len(self.type.hulls) > 1:
                    turrets = list(self.turrets)
                    turrets[turretPositionIdx] = (turretDescr, gunDescr)
                    hullDescr = self.__selectBestHull(turrets, self.chassis)
                return (gunDescr, turretDescr, hullDescr)

        return (None, None, None)

    def __setHullAndCall(self, hullDescr, callable):
        self.hull = hullDescr
        callable()

    def __initFromCompactDescr(self, compactDescr):
        unpack = struct.unpack
        try:
            type, components, optionalDeviceSlots, optionalDevices, emblemPositions, emblems, inscriptions, camouflages, horn = _splitVehicleCompactDescr(compactDescr)
            custNationID = type.customizationNationID
            customization = g_cache.customization(custNationID)
            self.type = type
            self.name = type.name
            self.level = type.level
            if IS_CLIENT or IS_CELLAPP:
                self.extras = type.extras
                self.extrasDict = type.extrasDict
            chassisID, engineID, fuelTankID, radioID = unpack('<4H', components[:8])
            self.chassis = _descrByID(type.chassis, chassisID)
            self.engine = _descrByID(type.engines, engineID)
            self.fuelTank = _descrByID(type.fuelTanks, fuelTankID)
            self.radio = _descrByID(type.radios, radioID)
            turrets = []
            for idx in xrange(len(type.turrets)):
                turretID, gunID = unpack('<2H', components[8 + idx * 4:12 + idx * 4])
                turret = _descrByID(type.turrets[idx], turretID)
                turrets.append((turret, _descrByID(turret['guns'], gunID)))

            self.turrets = turrets
            self.activeTurretPosition = 0
            if len(type.hulls) == 1:
                self.hull = type.hulls[0]
            else:
                self.hull = self.__selectBestHull(self.turrets, self.chassis)
            self.optionalDevices = [None] * NUM_OPTIONAL_DEVICE_SLOTS
            idx = NUM_OPTIONAL_DEVICE_SLOTS - 1
            while optionalDeviceSlots:
                if optionalDeviceSlots & 1:
                    self.optionalDevices[idx] = g_cache.optionalDevices()[unpack('<H', optionalDevices[:2])[0]]
                    optionalDevices = optionalDevices[2:]
                optionalDeviceSlots >>= 1
                idx -= 1

            if not emblemPositions & 15:
                self.playerEmblems = type._defEmblems
            else:
                emblemCache = g_cache.playerEmblems()[1]
                slots = [None,
                 None,
                 None,
                 None]
                for idx in _RANGE_4:
                    if emblemPositions & 1 << idx:
                        slots[idx] = _unpackIDAndDuration(emblems[:6])
                        emblems = emblems[6:]
                        emblemCache[slots[idx][0]]
                    slots[idx] = type._defEmblem

                self.playerEmblems = tuple(slots)
            if not emblemPositions & 240:
                self.playerInscriptions = _EMPTY_INSCRIPTIONS
            else:
                slots = [None,
                 None,
                 None,
                 None]
                for idx in _RANGE_4:
                    if emblemPositions & 1 << idx + 4:
                        slots[idx] = _unpackIDAndDuration(inscriptions[:6]) + (ord(inscriptions[6]),)
                        inscriptions = inscriptions[7:]
                        customization['inscriptions'][slots[idx][0]]
                        customization['inscriptionColors'][slots[idx][3]]
                    slots[idx] = _EMPTY_INSCRIPTION

                self.playerInscriptions = tuple(slots)
            if not camouflages:
                self.camouflages = _EMPTY_CAMOUFLAGES
            else:
                slots = list(_EMPTY_CAMOUFLAGES)
                while camouflages:
                    item = _unpackIDAndDuration(camouflages[:6])
                    camouflages = camouflages[6:]
                    idx = customization['camouflages'][item[0]]['kind']
                    if slots[idx][0] is not None:
                        LOG_WARNING('Second camouflage of same kind', custNationID, item[0], slots[idx][0])
                    slots[idx] = item

                self.camouflages = tuple(slots)
            self.__hornID = horn
            self.__updateAttributes()
        except Exception:
            LOG_ERROR('(compact descriptor to XML mismatch?)', compactDescr)
            raise

        return

    def __computeWeight(self):
        maxWeight = self.chassis['maxLoad']
        weight = self.hull['weight'] + self.chassis['weight'] + self.engine['weight'] + self.fuelTank['weight'] + self.radio['weight']
        for turretDescr, gunDescr in self.turrets:
            weight += turretDescr['weight'] + gunDescr['weight']

        vehWeightFraction = 0.0
        vehWeightAddition = 0.0
        for device in self.optionalDevices:
            if device is not None:
                fraction, addition, maxWeightChange = device.weightOnVehicle(self)
                vehWeightFraction += fraction
                vehWeightAddition += addition
                maxWeight += maxWeightChange

        return (weight * (1.0 + vehWeightFraction) + vehWeightAddition, maxWeight)

    def __haveIncompatibleOptionalDevices(self):
        for device in self.optionalDevices:
            if device is not None and not device.checkCompatibilityWithVehicle(self)[0]:
                return True

        return False

    def __updateAttributes(self):
        self.miscAttrs = None
        self.physics = None
        type = self.type
        chassis = self.chassis
        self.maxHealth = self.hull['maxHealth']
        for turretDescr, gunDescr in self.turrets:
            self.maxHealth += turretDescr['maxHealth']

        if IS_CLIENT or IS_BASEAPP or IS_WEB:
            bpl = type.balanceByComponentLevels
            modMul = g_cache.commonConfig['balanceModulesWeightMultipliers']
            vmw = g_cache.commonConfig['balanceByVehicleModule'].get(self.type.name, None)
            vehicleBalance = (vmw if vmw else bpl[self.level]) * modMul['vehicle']
            self.balanceWeight = (vehicleBalance + bpl[self.gun['level']] * modMul['gun'] + bpl[self.turret['level']] * modMul['turret'] + bpl[self.engine['level']] * modMul['engine'] + bpl[chassis['level']] * modMul['chassis'] + bpl[self.radio['level']] * modMul['radio']) * type.balanceByClass
        if IS_CLIENT or IS_CELLAPP or IS_WEB:
            weight, maxWeight = self.__computeWeight()
            trackCenterOffset = chassis['topRightCarryingPoint'][0]
            self.physics = {'weight': weight,
             'enginePower': self.engine['power'],
             'specificFriction': chassis['specificFriction'],
             'minPlaneNormalY': chassis['minPlaneNormalY'],
             'trackCenterOffset': trackCenterOffset,
             'rotationIsAroundCenter': chassis['rotationIsAroundCenter'],
             'speedLimits': self.type.speedLimits,
             'navmeshGirth': chassis['navmeshGirth'],
             'carryingTriangles': chassis['carryingTriangles'],
             'brakeForce': chassis['brakeForce'],
             'terrainResistance': chassis['terrainResistance']}
            self.miscAttrs = {'maxWeight': maxWeight,
             'repairSpeedFactor': 1.0,
             'additiveShotDispersionFactor': 1.0,
             'antifragmentationLiningFactor': 1.0,
             'circularVisionRadiusFactor': 1.0,
             'gunReloadTimeFactor': 1.0,
             'gunAimingTimeFactor': 1.0,
             'ammoBayHealthFactor': 1.0,
             'engineHealthFactor': 1.0,
             'chassisHealthFactor': 1.0,
             'vehicleByChassisDamageFactor': 1.0,
             'fuelTankHealthFactor': 1.0,
             'crewLevelIncrease': 0,
             'crewChanceToHitFactor': 1.0}
            for device in self.optionalDevices:
                if device is not None:
                    device.updateVehicleDescrAttrs(self)

            physics = self.physics
            defWeight = type.hulls[0]['weight'] + chassis['weight'] + type.engines[0]['weight'] + type.fuelTanks[0]['weight'] + type.radios[0]['weight']
            for turretList in type.turrets:
                defWeight += turretList[0]['weight'] + turretList[0]['guns'][0]['weight']

            defResistance = chassis['terrainResistance'][0]
            rotationEnergy = type.engines[0]['power'] * (weight / defWeight) / (chassis['rotationSpeed'] * defResistance)
            rotationSpeedLimit = physics['enginePower'] / (rotationEnergy * physics['terrainResistance'][0])
            if not chassis['rotationIsAroundCenter']:
                rotationEnergy -= trackCenterOffset * weight * chassis['specificFriction'] / defResistance
                if rotationEnergy <= 0.0:
                    raise Exception, 'wrong parameters of rotation of ' + type.name
            if chassis['rotationSpeedLimit'] is not None:
                rotationSpeedLimit = min(rotationSpeedLimit, chassis['rotationSpeedLimit'])
            physics['rotationSpeedLimit'] = rotationSpeedLimit
            physics['rotationEnergy'] = rotationEnergy
            if IS_CELLAPP or IS_DEVELOPMENT:
                invisibilityFactor = 1.0
                for turretDescr, _ in self.turrets:
                    invisibilityFactor *= turretDescr['invisibilityFactor']

                self.miscAttrs['invisibilityFactor'] = invisibilityFactor
        if IS_CELLAPP:
            hullPos = self.chassis['hullPosition']
            hullBboxMin, hullBboxMax, _ = self.hull['hitTester'].bbox
            turretPosOnHull = self.hull['turretPositions'][0]
            turretLocalTopY = max(hullBboxMax.y, turretPosOnHull.y + self.turret['hitTester'].bbox[1].y)
            gunPosOnHull = turretPosOnHull + self.turret['gunPosition']
            hullLocalCenterY = (hullBboxMin.y + hullBboxMax.y) / 2.0
            hullLocalPt1 = Vector3(0.0, hullLocalCenterY, hullBboxMax.z)
            hullLocalPt2 = Vector3(0.0, hullLocalCenterY, hullBboxMin.z)
            hullLocalCenterZ = (hullBboxMin.z + hullBboxMax.z) / 2.0
            hullLocalPt3 = Vector3(hullBboxMax.x, gunPosOnHull.y, hullLocalCenterZ)
            hullLocalPt4 = Vector3(hullBboxMin.x, gunPosOnHull.y, hullLocalCenterZ)
            self.visibilityCheckPoints = (Vector3(0.0, hullPos.y + turretLocalTopY, 0.0),
             hullPos + gunPosOnHull,
             hullPos + hullLocalPt1,
             hullPos + hullLocalPt2,
             hullPos + hullLocalPt3,
             hullPos + hullLocalPt4)
            self.observerPosOnChassis = Vector3(0, hullPos.y + turretLocalTopY, 0)
            self.observerPosOnTurret = self.turret['gunPosition']
        return


class VehicleType(object):

    def __init__(self, nationID, basicInfo, xmlPath):
        # type: (int, dict, str) -> None
        """Read vehicle type description from XML configuration."""
        self.name = basicInfo['name']
        self.id = (nationID, basicInfo['id'])
        self.compactDescr = basicInfo['compactDescr']
        self.historicalModelOf = basicInfo.get('historicalModelOf', self.compactDescr)
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        xmlCtx = (None, xmlPath)
        self.tags = basicInfo['tags']
        self.level = basicInfo['level']
        customizationNation = section.readString('customizationNation')
        if not customizationNation:
            self.customizationNationID = nationID
        else:
            self.customizationNationID = nations.INDICES.get(customizationNation)
            if self.customizationNationID is None:
                _xml.raiseWrongXml(xmlCtx, 'customizationNation', 'unknown nation name:' + customizationNation)
        self.speedLimits = (KMH_TO_MS * _xml.readPositiveFloat(xmlCtx, section, 'speedLimits/forward'), KMH_TO_MS * _xml.readPositiveFloat(xmlCtx, section, 'speedLimits/backward'))
        self.repairCost = _xml.readNonNegativeFloat(xmlCtx, section, 'repairCost')
        self.crewXpFactor = _xml.readNonNegativeFloat(xmlCtx, section, 'crewXpFactor')
        self.premiumVehicleXPFactor = 0.0
        if section.has_key('premiumVehicleXPFactor'):
            self.premiumVehicleXPFactor = _xml.readNonNegativeFloat(xmlCtx, section, 'premiumVehicleXPFactor')
        self.premiumVehicleXPFactor = max(self.premiumVehicleXPFactor, 0.0)
        if not IS_CLIENT or IS_DEVELOPMENT:
            self.xpFactor = 2.0 #_xml.readNonNegativeFloat(xmlCtx, section, 'xpFactor')
            self.creditsFactor = 2.0 #_xml.readNonNegativeFloat(xmlCtx, section, 'creditsFactor')
            self.freeXpFactor = 2.0 #_xml.readNonNegativeFloat(xmlCtx, section, 'freeXpFactor')
            self.healthBurnPerSec = 50 #_xml.readNonNegativeFloat(xmlCtx, section, 'healthBurnPerSec')
            self.healthBurnPerSecLossFraction = _DEFAULT_HEALTH_BURN_PER_SEC_LOSS_FRACTION
            self.invisibility = (1.0, 0.5) #(_xml.readFraction(xmlCtx, section, 'invisibility/moving'), _xml.readFraction(xmlCtx, section, 'invisibility/still'))
            self.invisibilityDeltas = {'camouflageBonus': 10.0, #_xml.readFraction(xmlCtx, section, 'invisibility/camouflageBonus'),
             'camouflageNetBonus': 25.0, #_xml.readFraction(xmlCtx, section, 'invisibility/camouflageNetBonus'),
             'firePenalty': 50.0} #_xml.readFraction(xmlCtx, section, 'invisibility/firePenalty')}
        self.crewRoles = _readCrew(xmlCtx, section, 'crew')
        commonConfig = g_cache.commonConfig
        if IS_CLIENT or IS_CELLAPP:
            self.extras = commonConfig['extras']
            self.extrasDict = commonConfig['extrasDict']
            self.devices = commonConfig['_devices']
            self.tankmen = _selectCrewExtras(self.crewRoles, self.extrasDict)
        if IS_CLIENT or IS_BASEAPP or IS_WEB:
            classTag = tuple(VEHICLE_CLASS_TAGS & self.tags)[0]
            self.balanceByClass = commonConfig['balanceByVehicleClasses'][classTag]
            self.balanceByComponentLevels = commonConfig['balanceByComponentLevels']
        if IS_CLIENT or IS_WEB:
            self.userString = basicInfo['userString']
            self.shortUserString = basicInfo['shortUserString']
            self.description = basicInfo['description']
        if IS_CLIENT:
            self.damageStickersLodDist = commonConfig['miscParams']['damageStickersLodDist']
            collisionVelCfg = commonConfig['miscParams']['collisionEffectVelocities']
            self.heavyCollisionEffectVelocities = {'hull': collisionVelCfg['hull'][1],
             'track': collisionVelCfg['track'][1],
             'waterContact': collisionVelCfg['waterContact'][1]}
            self.effects = _readVehicleEffects(xmlCtx, section, 'effects', commonConfig['defaultVehicleEffects'])
            self.camouflageTiling, self.camouflageExclusionMask = _readCamouflageTilingAndMask(xmlCtx, section, 'camouflage')
            self.emblemsLodDist = _readLodDist(xmlCtx, section, 'emblems/lodDist')
            self.emblemsAlpha = _xml.readFraction(xmlCtx, section, 'emblems/alpha')
            self._prereqs = None
        if IS_CELLAPP or IS_CLIENT:
            collisionVelCfg = commonConfig['miscParams']['collisionEffectVelocities']
            self.collisionEffectVelocities = {'hull': collisionVelCfg['hull'][0],
             'track': collisionVelCfg['track'][0],
             'waterContact': collisionVelCfg['waterContact'][0],
             'ramming': collisionVelCfg['ramming']}
        defEmblemName = _xml.readNonEmptyString(xmlCtx, section, 'emblems/default')
        self.defaultPlayerEmblemID = g_cache.playerEmblems()[2].get(defEmblemName)
        if self.defaultPlayerEmblemID is None:
            _xml.raiseWrongXml(xmlCtx, 'emblems/default', "unknown emblem '%s'" % defEmblemName)
        self._defEmblem = (self.defaultPlayerEmblemID, _CUSTOMIZATION_EPOCH, 0)
        self._defEmblems = (self._defEmblem,
         self._defEmblem,
         self._defEmblem,
         self._defEmblem)
        hornPriceFactor, self.hornDistanceFactor, self.hornVolumeFactor = _readVehicleHorns(xmlCtx, section, 'horns')
        pricesDest = _g_prices
        if pricesDest is not None:
            pricesDest['vehicleCamouflagePriceFactors'][self.compactDescr] = _xml.readNonNegativeFloat(xmlCtx, section, 'camouflage/priceFactor')
            pricesDest['vehicleHornPriceFactors'][self.compactDescr] = hornPriceFactor
        unlocksDescrs = []
        self.unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs)
        defHull = _readHull((xmlCtx, 'hull'), _xml.getSubsection(xmlCtx, section, 'hull'))
        self.chassis = _readInstallableComponents(xmlCtx, section, 'chassis', nationID, _readChassis, _readChassisLocals, g_cache.chassis(nationID), g_cache.chassisIDs(nationID), unlocksDescrs)
        self.engines = _readInstallableComponents(xmlCtx, section, 'engines', nationID, _readEngine, _defaultLocalReader, g_cache.engines(nationID), g_cache.engineIDs(nationID), unlocksDescrs)
        self.fuelTanks = _readInstallableComponents(xmlCtx, section, 'fuelTanks', nationID, _readFuelTank, _defaultLocalReader, g_cache.fuelTanks(nationID), g_cache.fuelTankIDs(nationID), unlocksDescrs)
        self.radios = _readInstallableComponents(xmlCtx, section, 'radios', nationID, _readRadio, _defaultLocalReader, g_cache.radios(nationID), g_cache.radioIDs(nationID), unlocksDescrs)
        turretsList = []
        for n in xrange(len(defHull['turretPositions'])):
            turrets = _readInstallableComponents(xmlCtx, section, 'turrets' + repr(n), nationID, _readTurret, _readTurretLocals, g_cache.turrets(nationID), g_cache.turretIDs(nationID), unlocksDescrs)
            turretsList.append(turrets)

        self.turrets = tuple(turretsList)
        self.hulls = (defHull,)
        if section.has_key('hull/variants'):
            self.hulls += _readHullVariants((xmlCtx, 'hull/variants'), section['hull/variants'], defHull, self.chassis, self.turrets)
        compactDescrs = set()
        _collectComponents(compactDescrs, self.chassis)
        _collectComponents(compactDescrs, self.engines)
        _collectComponents(compactDescrs, self.fuelTanks)
        _collectComponents(compactDescrs, self.radios)
        for turrets in self.turrets:
            _collectComponents(compactDescrs, turrets)
            for turret in turrets:
                _collectComponents(compactDescrs, turret['guns'])

        self.installableComponents = compactDescrs
        self.unlocksDescrs = self.__convertAndValidateUnlocksDescrs(unlocksDescrs)
        self.autounlockedItems = self.__collectDefaultUnlocks()
        section = None
        ResMgr.purge(xmlPath, True)
        return

    def __convertAndValidateUnlocksDescrs(self, srcList):
        nationID = self.id[0]
        destList = []
        reqItems = {}
        for descr in srcList:
            itemTypeName = descr[1]
            itemName = descr[2]
            itemID = None
            try:
                if itemTypeName == 'vehicle':
                    itemID = g_list.getIDsByName(nations.NAMES[nationID] + ':' + itemName)[1]
                if itemTypeName == 'vehicleChassis':
                    itemID = g_cache.chassisIDs(nationID)[itemName]
                if itemTypeName == 'vehicleTurret':
                    itemID = g_cache.turretIDs(nationID)[itemName]
                if itemTypeName == 'vehicleGun':
                    itemID = g_cache.gunIDs(nationID)[itemName]
                if itemTypeName == 'vehicleEngine':
                    itemID = g_cache.engineIDs(nationID)[itemName]
                if itemTypeName == 'vehicleFuelTank':
                    itemID = g_cache.fuelTankIDs(nationID)[itemName]
                if itemTypeName == 'vehicleRadio':
                    itemID = g_cache.radioIDs(nationID)[itemName]
            except Exception:
                LOG_CURRENT_EXCEPTION()
                raise Exception, "wrong name '%s' in <unlocks> of '%s'" % (itemName, self.name)

            compactDescr = makeIntCompactDescrByID(itemTypeName, nationID, itemID)
            if itemTypeName != 'vehicle' and compactDescr not in self.installableComponents:
                raise Exception, "component '%s' in <unlocks> is not for '%s'" % (itemName, self.name)
            reqItems.setdefault(compactDescr, set()).update(descr[3:])
            destList.append((descr[0], compactDescr))

        for descr in reqItems.itervalues():
            for compactDescr in tuple(descr):
                _collectReqItemsRecursively(descr, tuple(reqItems.get(compactDescr, ())), reqItems)

        for idx in xrange(len(destList)):
            descr = destList[idx]
            destList[idx] = descr + tuple(reqItems[descr[1]])

        return destList

    def __collectDefaultUnlocks(self):
        autounlocks = []
        autounlocks.append(self.chassis[0]['compactDescr'])
        autounlocks.append(self.engines[0]['compactDescr'])
        autounlocks.append(self.fuelTanks[0]['compactDescr'])
        autounlocks.append(self.radios[0]['compactDescr'])
        for posIndex, turrets in enumerate(self.turrets):
            turret = turrets[0]
            autounlocks.append(turret['compactDescr'])
            autounlocks.append(turret['guns'][0]['compactDescr'])
            if posIndex in self.hulls[0]['fakeTurrets']['lobby']:
                for turret in turrets[1:]:
                    autounlocks.append(turret['compactDescr'])

        return autounlocks


class Cache(object):

    def __init__(self):
        # type: () -> None
        """Initialize empty vehicle component caches."""
        self.__vehicles = {}
        self.__commonConfig = None
        self.__chassis = [ None for i in nations.NAMES ]
        self.__engines = [ None for i in nations.NAMES ]
        self.__fuelTanks = [ None for i in nations.NAMES ]
        self.__radios = [ None for i in nations.NAMES ]
        self.__turrets = [ None for i in nations.NAMES ]
        self.__guns = [ None for i in nations.NAMES ]
        self.__shells = [ None for i in nations.NAMES ]
        self.__optionalDevices = None
        self.__optionalDeviceIDs = None
        self.__equipments = None
        self.__equipmentIDs = None
        self.__chassisIDs = [ None for i in nations.NAMES ]
        self.__engineIDs = [ None for i in nations.NAMES ]
        self.__fuelTankIDs = [ None for i in nations.NAMES ]
        self.__radioIDs = [ None for i in nations.NAMES ]
        self.__turretIDs = [ None for i in nations.NAMES ]
        self.__gunIDs = [ None for i in nations.NAMES ]
        self.__shellIDs = [ None for i in nations.NAMES ]
        self.__customization = [ None for i in nations.NAMES ]
        self.__horns = None
        self.__playerEmblems = None
        self.__shotEffects = None
        self.__shotEffectsIndexes = None
        self.__damageStickers = None
        if IS_CLIENT:
            self.__vehicleEffects = None
            self.__gunEffects = None
            self.__chassisEffects = None
            self.__exhaustEffects = None
            self.__turretDetachmentEffects = None
        return

    def clearPrereqs(self):
        # type: () -> None
        """Stub for API compatibility."""
        pass

    def vehicle(self, nationID, vehicleTypeID):
        # type: (int, int) -> object
        """Return :class:`VehicleType` instance for given nation and id."""
        id = (nationID, vehicleTypeID)
        vt = self.__vehicles.get(id)
        if vt:
            return vt
        nation = nations.NAMES[nationID]
        basicInfo = g_list.getList(nationID)[vehicleTypeID]
        xmlName = basicInfo['name'].split(':')[1]
        xmlPath = _VEHICLE_TYPE_XML_PATH + nation + '/' + xmlName + '.xml'
        vt = VehicleType(nationID, basicInfo, xmlPath)
        self.__vehicles[id] = vt
        return vt

    def chassis(self, nationID):
        # type: (int) -> dict
        """Return cached chassis descriptors for a nation."""
        return self.__getList(nationID, 'chassis')

    def chassisIDs(self, nationID):
        # type: (int) -> dict
        """Return mapping of chassis names to ids."""
        return self.__getList(nationID, 'chassisIDs')

    def engines(self, nationID):
        # type: (int) -> dict
        """Return engine descriptors for a nation."""
        return self.__getList(nationID, 'engines')

    def engineIDs(self, nationID):
        # type: (int) -> dict
        """Return mapping of engine names to ids."""
        return self.__getList(nationID, 'engineIDs')

    def fuelTanks(self, nationID):
        # type: (int) -> dict
        """Return fuel tank descriptors for a nation."""
        return self.__getList(nationID, 'fuelTanks')

    def fuelTankIDs(self, nationID):
        # type: (int) -> dict
        """Return mapping of fuel tank names to ids."""
        return self.__getList(nationID, 'fuelTankIDs')

    def radios(self, nationID):
        # type: (int) -> dict
        """Return radio descriptors for a nation."""
        return self.__getList(nationID, 'radios')

    def radioIDs(self, nationID):
        # type: (int) -> dict
        """Return mapping of radio names to ids."""
        return self.__getList(nationID, 'radioIDs')

    def turrets(self, nationID):
        # type: (int) -> dict
        """Return turret descriptors for a nation."""
        return self.__getList(nationID, 'turrets')

    def turretIDs(self, nationID):
        # type: (int) -> dict
        """Return mapping of turret names to ids."""
        return self.__getList(nationID, 'turretIDs')

    def guns(self, nationID):
        # type: (int) -> dict
        """Return gun descriptors for a nation."""
        return self.__getList(nationID, 'guns')

    def gunIDs(self, nationID):
        # type: (int) -> dict
        """Return mapping of gun names to ids."""
        return self.__getList(nationID, 'gunIDs')

    def shells(self, nationID):
        # type: (int) -> dict
        """Return shell descriptors for a nation."""
        return self.__getList(nationID, 'shells')

    def shellIDs(self, nationID):
        # type: (int) -> dict
        """Return mapping of shell names to ids."""
        return self.__getList(nationID, 'shellIDs')

    def customization(self, nationID):
        # type: (int) -> dict
        """Return customization data for the given nation."""
        descr = self.__customization[nationID]
        if descr is None:
            nationName = nations.NAMES[nationID]
            descr = {}
            if nationName in nations.AVAILABLE_NAMES:
                commonDescr = _readCustomization(_VEHICLE_TYPE_XML_PATH + 'common/customization.xml', nationID, idsRange=(5001, 65535))
                customDescr = _readCustomization(_VEHICLE_TYPE_XML_PATH + nationName + '/customization.xml', nationID, idsRange=(1, 5000))
                descr = _joinCustomizationParams(nationID, commonDescr, customDescr)
            self.__customization[nationID] = descr
        return descr

    def horns(self):
        # type: () -> dict
        """Load and cache horn descriptors."""
        descr = self.__horns
        if descr is None:
            descr = self.__horns = _readHorns(_VEHICLE_TYPE_XML_PATH + 'common/horns.xml')
        return descr

    def playerEmblems(self):
        # type: () -> tuple
        """Return player emblem groups and related data."""
        descr = self.__playerEmblems
        if descr is None:
            descr = self.__playerEmblems = _readPlayerEmblems(_VEHICLE_TYPE_XML_PATH + 'common/player_emblems.xml')
        return descr

    def optionalDevices(self):
        # type: () -> dict
        """Return optional device descriptors."""
        descr = self.__optionalDevices
        if descr is None:
            from items import artefacts
            self.__optionalDevices, self.__optionalDeviceIDs = _readArtefacts(_VEHICLE_TYPE_XML_PATH + 'common/optional_devices.xml')
            descr = self.__optionalDevices
        return descr

    def optionalDeviceIDs(self):
        # type: () -> dict
        """Return mapping of optional device names to ids."""
        descr = self.__optionalDeviceIDs
        if descr is None:
            from items import artefacts
            self.__optionalDevices, self.__optionalDeviceIDs = _readArtefacts(_VEHICLE_TYPE_XML_PATH + 'common/optional_devices.xml')
            descr = self.__optionalDeviceIDs
        return descr

    def equipments(self):
        # type: () -> dict
        """Return equipment descriptors."""
        descr = self.__equipments
        if descr is None:
            from items import artefacts
            self.__equipments, self.__equipmentIDs = _readArtefacts(_VEHICLE_TYPE_XML_PATH + 'common/equipments.xml')
            descr = self.__equipments
        return descr

    def equipmentIDs(self):
        # type: () -> dict
        """Return mapping of equipment names to ids."""
        descr = self.__equipmentIDs
        if descr is None:
            from items import artefacts
            self.__equipments, self.__equipmentIDs = _readArtefacts(_VEHICLE_TYPE_XML_PATH + 'common/equipments.xml')
            descr = self.__equipmentIDs
        return descr

    @property
    def shotEffects(self):
        # type: () -> dict
        """Return shot effect descriptors."""
        descr = self.__shotEffects
        if descr is None:
            self.__shotEffectsIndexes, self.__shotEffects = _readShotEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/shot_effects.xml')
            descr = self.__shotEffects
        return descr

    @property
    def shotEffectsIndexes(self):
        # type: () -> dict
        """Return mapping from effect names to indexes."""
        descr = self.__shotEffectsIndexes
        if descr is None:
            self.__shotEffectsIndexes, self.__shotEffects = _readShotEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/shot_effects.xml')
            descr = self.__shotEffectsIndexes
        return descr

    @property
    def damageStickers(self):
        # type: () -> dict
        """Return damage sticker configuration."""
        descr = self.__damageStickers
        if descr is None:
            descr = self.__damageStickers = _readDamageStickers(_VEHICLE_TYPE_XML_PATH + 'common/damage_stickers.xml')
        return descr

    @property
    def commonConfig(self):
        # type: () -> dict
        """Load and cache common vehicle configuration."""
        descr = self.__commonConfig
        if descr is None:
            commonXmlPath = _VEHICLE_TYPE_XML_PATH + 'common/vehicle.xml'
            commonXml = ResMgr.openSection(commonXmlPath)
            if commonXml is None:
                _xml.raiseWrongXml(None, commonXmlPath, 'can not open or read')
            descr = self.__commonConfig = _readCommonConfig((None, commonXmlPath), commonXml)
            hornCooldownParams = self.__commonConfig['miscParams']['hornCooldown']
            HORN_COOLDOWN.WINDOW = hornCooldownParams['window']
            HORN_COOLDOWN.CLIENT_WINDOW_EXPANSION = hornCooldownParams['clientWindowExpansion']
            HORN_COOLDOWN.MAX_SIGNALS = hornCooldownParams['maxSignals']
            commonXml = None
            ResMgr.purge(commonXmlPath, True)
        return descr

    @property
    def _vehicleEffects(self):
        if self.__vehicleEffects is None:
            self.__vehicleEffects = _readEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/vehicle_effects.xml', True)
        return self.__vehicleEffects

    @property
    def _gunEffects(self):
        if self.__gunEffects is None:
            self.__gunEffects = _readEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/gun_effects.xml')
        return self.__gunEffects

    @property
    def _exhaustEffects(self):
        if self.__exhaustEffects is None:
            self.__exhaustEffects = _readExhaustEffectsGroups(_VEHICLE_TYPE_XML_PATH + 'common/exhaust_effects.xml')
        return self.__exhaustEffects

    @property
    def _chassisEffects(self):
        if self.__chassisEffects is None:
            self.__chassisEffects = _readChassisEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/chassis_effects.xml')
        return self.__chassisEffects

    @property
    def _turretDetachmentEffects(self):
        if self.__turretDetachmentEffects is None:
            self.__turretDetachmentEffects = _readEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/turret_effects.xml')
        return self.__turretDetachmentEffects

    def __getList(self, nationID, listName):
        nations = getattr(self, '_Cache__' + listName)
        if nations[nationID] is None:
            self.__readNation(nationID)
        return nations[nationID]

    def __readNation(self, nationID):
        nationName = nations.NAMES[nationID]
        if nationName not in nations.AVAILABLE_NAMES:
            emptyDict = {}
            self.__chassis[nationID], self.__chassisIDs[nationID] = emptyDict, emptyDict
            self.__engines[nationID], self.__engineIDs[nationID] = emptyDict, emptyDict
            self.__fuelTanks[nationID], self.__fuelTankIDs[nationID] = emptyDict, emptyDict
            self.__radios[nationID], self.__radioIDs[nationID] = emptyDict, emptyDict
            self.__turrets[nationID], self.__turretIDs[nationID] = emptyDict, emptyDict
            self.__guns[nationID], self.__gunIDs[nationID] = emptyDict, emptyDict
            self.__shells[nationID], self.__shellIDs[nationID] = emptyDict, emptyDict
            return
        compsXmlPath = _VEHICLE_TYPE_XML_PATH + nationName + '/components/'
        self.__chassis[nationID], self.__chassisIDs[nationID] = _readComponents(compsXmlPath + 'chassis.xml', _readChassis, nationID, 'vehicleChassis')
        self.__engines[nationID], self.__engineIDs[nationID] = _readComponents(compsXmlPath + 'engines.xml', _readEngine, nationID, 'vehicleEngine')
        self.__fuelTanks[nationID], self.__fuelTankIDs[nationID] = _readComponents(compsXmlPath + 'fuelTanks.xml', _readFuelTank, nationID, 'vehicleFuelTank')
        self.__radios[nationID], self.__radioIDs[nationID] = _readComponents(compsXmlPath + 'radios.xml', _readRadio, nationID, 'vehicleRadio')
        self.__shells[nationID], self.__shellIDs[nationID] = _readShells(compsXmlPath + 'shells.xml', nationID)
        self.__guns[nationID], self.__gunIDs[nationID] = _readComponents(compsXmlPath + 'guns.xml', _readGun, nationID, 'vehicleGun')
        self.__turrets[nationID], self.__turretIDs[nationID] = _readComponents(compsXmlPath + 'turrets.xml', _readTurret, nationID, 'vehicleTurret')

    def __idsFromNames(self, descrs):
        return dict(((d['name'], d['id']) for d in descrs.itervalues()))


class VehicleList(object):

    def __init__(self):
        # type: () -> None
        """Read vehicle lists for all nations."""
        self.__ids = {}
        list = []
        for nation in nations.NAMES:
            if nation not in nations.AVAILABLE_NAMES:
                list.append({})
                continue
            xmlPath = _VEHICLE_TYPE_XML_PATH + nation + '/list.xml'
            section = ResMgr.openSection(xmlPath)
            if section is None:
                _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
            descrs = self.__readVehicleList(nation, section, xmlPath)
            list.append(descrs)
            nationID = nations.INDICES[nation]
            self.__ids.update(dict(((d['name'], (nationID, d['id'])) for d in descrs.itervalues())))
            ResMgr.purge(xmlPath, True)

        self.__nations = tuple(list)
        return

    def getList(self, nationID):
        # type: (int) -> dict
        """Return dictionary of vehicle descriptors for a nation."""
        return self.__nations[nationID]

    def isVehicleExisting(self, name):
        # type: (str) -> bool
        """Check if vehicle with given name exists in any nation."""
        return name in self.__ids

    def getIDsByVehName(self, name):
        # type: (str) -> tuple
        """Return nation and id pair for vehicle short name."""
        for nation in nations.NAMES:
            fullName = '%s:%s' % (nation, name)
            if fullName in self.__ids:
                return self.__ids[fullName]

        raise Exception, "unknown vehicle name '%s'" % name

    def getIDsByName(self, name):
        # type: (str) -> tuple
        """Return nation and id pair for full vehicle type name."""
        ids = self.__ids.get(name)
        if ids is None:
            raise Exception, "unknown vehicle type name '%s'" % name
        return ids

    def __readVehicleList(self, nation, section, xmlPath):
        res = {}
        ids = {}
        historicalModelsOf = {}
        nationID = nations.INDICES[nation]
        pricesDest = _g_prices
        if pricesDest is not None:
            SELL_PRICE_FACTOR = 0.5
        for vname, vsection in section.items():
            ctx = (None, xmlPath + '/' + vname)
            if vname in ids:
                _xml.raiseWrongXml(ctx, '', 'vehicle type name is not unique')
            id = _xml.readInt(ctx, vsection, 'id', 0, 255)
            if id in res:
                _xml.raiseWrongXml(ctx, 'id', 'is not unique')
            compactDescr = makeIntCompactDescrByID('vehicle', nationID, id)
            ids[vname] = id
            res[id] = {'name': nation + ':' + vname,
             'id': id,
             'compactDescr': compactDescr,
             'level': _readLevel(ctx, vsection)}
            tags = _readTags(ctx, vsection, 'tags', 'vehicle')
            if 1 != len(tags & VEHICLE_CLASS_TAGS):
                _xml.raiseWrongXml(ctx, 'tags', 'vehicle class tag is missing or is multiple')
            if vsection.has_key('historicalModelOf'):
                if len(tags & OBLIGATORY_HB_TAGS) != 3:
                    _xml.raiseWrongXml(ctx, 'tags', 'vehicle with tag <historicalModelOf> must contain secret, cannot_be_sold and historical_battles tags')
                historicalModelsOf[id] = vsection.readString('historicalModelOf')
            res[id]['tags'] = tags
            if IS_CLIENT or IS_WEB:
                res[id]['userString'] = i18n.makeString(vsection.readString('userString'))
                res[id]['description'] = i18n.makeString(vsection.readString('description'))
                res[id]['shortUserString'] = i18n.makeString(vsection.readString('shortUserString'))
                if not res[id]['shortUserString']:
                    res[id]['shortUserString'] = res[id]['userString']
            price = _xml.readPrice(ctx, vsection, 'price')
            if price[1]:
                res[id]['tags'] |= frozenset(('premium',))
            if pricesDest is not None:
                pricesDest['itemPrices'][compactDescr] = price
                if vsection.readBool('notInShop', False):
                    pricesDest['notInShopItems'].add(compactDescr)
                if IS_RENTALS_ENABLED and vsection.readBool('cannotBeBought', False):
                    pricesDest['vehiclesNotToBuy'].add(compactDescr)
                sellPriceFactor = vsection.readFloat('sellPriceFactor', SELL_PRICE_FACTOR)
                if abs(sellPriceFactor - SELL_PRICE_FACTOR) > 0.001:
                    pricesDest['vehicleSellPriceFactors'][compactDescr] = sellPriceFactor
                if price[1] and vsection.readBool('sellForGold', False):
                    pricesDest['vehiclesToSellForGold'].add(compactDescr)
                rentPrice = _xml.readRentPrice(ctx, vsection, 'rent') if IS_RENTALS_ENABLED else {}
                pricesDest['vehiclesRentPrices'][compactDescr] = rentPrice

        for histModelID, baseModelName in historicalModelsOf.iteritems():
            compactDescr = makeIntCompactDescrByID('vehicle', nationID, histModelID)
            if pricesDest is not None and compactDescr not in pricesDest['notInShopItems']:
                _xml.raiseWrongXml(ctx, 'notInShop', 'Historical model %s must contain notInShop tag equals to True' % res[histModelID]['name'])
            if baseModelName not in ids:
                _xml.raiseWrongXml(ctx, 'historicalModelOf', 'Invalid base vehicle %s for historical model %s' % (baseModelName, res[histModelID]['name']))
            baseID = ids[baseModelName]
            if res[baseID]['tags'] - res[histModelID]['tags'] - OBLIGATORY_HB_TAGS:
                _xml.raiseWrongXml(ctx, 'tags', 'Historical model %s must contain the same tags as base vehicle %s' % (res[histModelID]['name'], baseModelName))
            res[histModelID]['historicalModelOf'] = makeIntCompactDescrByID('vehicle', nationID, baseID)

        return res


def makeIntCompactDescrByID(itemTypeName, nationID, itemID):
    # type: (str, int, int) -> int
    """Build integer compact descriptor from item identifiers."""
    header = items.ITEM_TYPES[itemTypeName] + (nationID << 4)
    return (itemID << 8) + header


def parseIntCompactDescr(compactDescr):
    # type: (int) -> tuple
    """Split integer compact descriptor into type, nation and id."""
    return (compactDescr & 15, compactDescr >> 4 & 15, compactDescr >> 8 & 65535)


def parseVehicleCompactDescr(compactDescr):
    # type: (str) -> tuple
    """Return nation and vehicle type id from packed descriptor."""
    header, vehicleTypeID = struct.unpack('2B', compactDescr[0:2])
    return (header >> 4 & 15, vehicleTypeID)


__ITEM_TYPE_VEHICLE = items.ITEM_TYPES.vehicle

def getVehicleTypeCompactDescr(compactDescr):
    # type: (str) -> int
    """Return compact descriptor for vehicle type only."""
    nationID, vehicleTypeID = parseVehicleCompactDescr(compactDescr)
    return __ITEM_TYPE_VEHICLE + (nationID << 4) + (vehicleTypeID << 8)


def getDictDescr(compactDescr):
    # type: (int) -> dict
    """Return descriptor dictionary for given compact descriptor."""
    try:
        itemTypeID = compactDescr & 15
        nationID = compactDescr >> 4 & 15
        compTypeID = compactDescr >> 8 & 65535
        itemTypeName = items.ITEM_TYPE_NAMES[itemTypeID]
        return _dictDescrGetters[itemTypeName](nationID, compTypeID)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_ERROR('(compact description to XML mismatch?)', compactDescr)
        raise


_dictDescrGetters = {'shell': lambda nationID, compTypeID: g_cache.shells(nationID)[compTypeID],
 'equipment': lambda nationID, compTypeID: g_cache.equipments()[compTypeID],
 'optionalDevice': lambda nationID, compTypeID: g_cache.optionalDevices()[compTypeID],
 'vehicleGun': lambda nationID, compTypeID: g_cache.guns(nationID)[compTypeID],
 'vehicleTurret': lambda nationID, compTypeID: g_cache.turrets(nationID)[compTypeID],
 'vehicleEngine': lambda nationID, compTypeID: g_cache.engines(nationID)[compTypeID],
 'vehicleRadio': lambda nationID, compTypeID: g_cache.radios(nationID)[compTypeID],
 'vehicleChassis': lambda nationID, compTypeID: g_cache.chassis(nationID)[compTypeID],
 'vehicleFuelTank': lambda nationID, compTypeID: g_cache.fuelTanks(nationID)[compTypeID]}

def getVehicleType(compactDescr):
    # type: (object) -> VehicleType
    """Return :class:`VehicleType` for compact descriptor or integer."""
    cdType = type(compactDescr)
    if cdType is types.IntType or cdType is types.LongType:
        nationID = compactDescr >> 4 & 15
        vehicleTypeID = compactDescr >> 8 & 65535
    else:
        header, vehicleTypeID = struct.unpack('2B', compactDescr[0:2])
        nationID = header >> 4 & 15
    return g_cache.vehicle(nationID, vehicleTypeID)


def getVehicleClass(compactDescr):
    # type: (object) -> str
    """Return vehicle class tag for compact descriptor."""
    for vehClass in VEHICLE_CLASS_TAGS & getVehicleType(compactDescr).tags:
        return vehClass

    assert False


def stripCustomizationFromVehicleCompactDescr(compactDescr, stripEmblems=True, stripInscriptions=True, stripCamouflages=True, keepInfinite=False):
    # type: (str, bool, bool, bool, bool) -> tuple
    """Remove customization info from vehicle compact descriptor."""
    type, components, optionalDevicesSlots, optionalDevices, emblemSlots, emblems, inscriptions, camouflages, horn = _splitVehicleCompactDescr(compactDescr)
    resEmblems = {}
    if stripEmblems and emblems:
        remainedEmblems = ''
        for pos in _RANGE_4:
            if emblemSlots & 1 << pos:
                emblemInfo = _unpackIDAndDuration(emblems[:6])
                if keepInfinite and emblemInfo[2] == 0:
                    remainedEmblems += emblems[:6]
                else:
                    resEmblems[pos] = emblemInfo
                    emblemSlots &= ~(1 << pos)
                emblems = emblems[6:]

        emblems = remainedEmblems
    resInscrs = {}
    if stripInscriptions and inscriptions:
        remainedInscriptions = ''
        for pos in _RANGE_4:
            if emblemSlots & 1 << pos + 4:
                inscrInfo = _unpackIDAndDuration(inscriptions[:6]) + (ord(inscriptions[6]),)
                if keepInfinite and inscrInfo[2] == 0:
                    remainedInscriptions += inscriptions[:7]
                else:
                    resInscrs[pos] = inscrInfo
                    emblemSlots &= ~(1 << pos + 4)
                inscriptions = inscriptions[7:]

        inscriptions = remainedInscriptions
    resCams = {}
    if stripCamouflages and camouflages:
        remainedCamouflages = ''
        pos = 0
        while camouflages:
            camInfo = _unpackIDAndDuration(camouflages[:6])
            if keepInfinite and camInfo[2] == 0:
                remainedCamouflages += camouflages[:6]
            else:
                resCams[pos] = camInfo
            camouflages = camouflages[6:]
            pos += 1

        camouflages = remainedCamouflages
    compactDescr = _combineVehicleCompactDescr(type, components, optionalDevicesSlots, optionalDevices, emblemSlots, emblems, inscriptions, camouflages, horn)
    return (compactDescr,
     resEmblems,
     resInscrs,
     resCams)


def isShellSuitableForGun(shellCompactDescr, gunDescr):
    # type: (int, dict) -> bool
    """Check whether shell can be fired by the given gun."""
    itemTypeID, nationID, shellTypeID = parseIntCompactDescr(shellCompactDescr)
    assert itemTypeID == items.ITEM_TYPES.shell
    shellID = (nationID, shellTypeID)
    for shotDescr in gunDescr['shots']:
        if shotDescr['shell']['id'] == shellID:
            return True

    return False


def getEmptyAmmoForGun(gunDescr):
    # type: (dict) -> list
    """Return an empty ammo layout for the gun."""
    ammo = []
    for shot in gunDescr['shots']:
        ammo.append(shot['shell']['compactDescr'])
        ammo.append(0)

    if not ammo:
        ammo.append(gunDescr['shots'][0]['shell']['compactDescr'])
        ammo.append(0)
    return ammo


def getDefaultAmmoForGun(gunDescr):
    # type: (dict) -> list
    """Return default ammo setup for the gun."""
    return _getAmmoForGun(gunDescr, None)


def getUniformAmmoForGun(gunDescr):
    # type: (dict) -> list
    """Return ammo where all shell types have an equal share."""
    shots = len(gunDescr['shots'])
    defaultPortion = 1.0 / shots if shots else 1.0
    return _getAmmoForGun(gunDescr, defaultPortion)


def _getAmmoForGun(gunDescr, defaultPortion=None):
    # type: (dict, float or None) -> list
    ammo = []
    maxCount = gunDescr['maxAmmo']
    clipSize = gunDescr['clip'][0]
    currCount = 0
    for shot in gunDescr['shots']:
        if defaultPortion is None:
            portion = shot['defaultPortion']
        else:
            portion = defaultPortion
        shotCount = int(portion * maxCount / clipSize + 0.5) * clipSize
        if currCount + shotCount > maxCount:
            shotCount = maxCount - currCount
        currCount += shotCount
        ammo.append(shot['shell']['compactDescr'])
        ammo.append(shotCount)

    if not ammo:
        ammo.append(gunDescr['shots'][0]['shell']['compactDescr'])
        ammo.append(maxCount)
    return ammo


def getUnlocksSources():
    # type: () -> dict
    """Return mapping from item CDs to vehicle types unlocking them."""
    res = {}
    for nationID in xrange(len(nations.NAMES)):
        for vehicleTypeID in g_list.getList(nationID).iterkeys():
            vehicleType = g_cache.vehicle(nationID, vehicleTypeID)
            for descr in vehicleType.unlocksDescrs:
                cd = descr[1]
                res.setdefault(cd, set()).add(vehicleType)

    return res


def _readComponents(xmlPath, reader, nationID, itemTypeName):
    # type: (str, object, int, str) -> tuple
    """Read component descriptors from XML file."""
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    descrs = {}
    ids = {}
    for name in _xml.getSubsection(xmlCtx, section, 'ids').keys():
        name = intern(name)
        id = _xml.readInt(xmlCtx, section, 'ids/' + name, 0, 65535)
        if descrs.has_key(id):
            _xml.raiseWrongXml(xmlCtx, 'ids/' + name, 'name or ID is not unique')
        ids[name] = id
        descrs[id] = {'itemTypeName': itemTypeName,
         'name': name,
         'id': (nationID, id),
         'compactDescr': makeIntCompactDescrByID(itemTypeName, nationID, id),
         'status': 'empty'}

    for name, subsection in _xml.getChildren(xmlCtx, section, 'shared'):
        ctx = (xmlCtx, 'shared')
        id = ids.get(name)
        if id is None:
            _xml.raiseWrongXml(ctx, name, 'unknown name')
        descr = descrs[id]
        if descr['status'] != 'empty':
            _xml.raiseWrongXml(ctx, name, 'already defined')
        descr.update(reader((ctx, name), subsection, descr['compactDescr']))
        descr['status'] = 'shared'

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return (descrs, ids)


def _readInstallableComponents(xmlCtx, section, subsectionName, nationID, reader, localReader, cachedDescrs, cachedIDs, unlocksDescrs, parentItem=None):
    # type: (tuple, object, str, int, callable, callable, dict, dict, list, object or None) -> tuple
    """Parse components that can be installed on a vehicle.

    :param xmlCtx: context for XML error messages.
    :param section: owning XML section.
    :param subsectionName: name of subsection containing component refs.
    :param nationID: nation index the components belong to.
    :param reader: callable parsing shared component data.
    :param localReader: callable parsing local overrides.
    :param cachedDescrs: dictionary with shared descriptors.
    :param cachedIDs: mapping from component names to ids.
    :param unlocksDescrs: list collecting unlock descriptors.
    :param parentItem: optional parent item used by readers.
    :return: tuple of descriptors for each component found.
    """
    res = []
    for sname, subsection in _xml.getChildren(xmlCtx, section, subsectionName):
        ctx = (xmlCtx, subsectionName + '/' + sname)
        id = cachedIDs.get(sname)
        if id is None:
            _xml.raiseWrongXml(ctx, '', 'unknown name')
        descr = cachedDescrs[id]
        if subsection.asString == 'shared':
            if descr['status'] != 'shared':
                _xml.raiseWrongXml(ctx, sname, 'the component is not shared')
            res.append(localReader(ctx, subsection, descr, unlocksDescrs, parentItem))
        if descr['status'] != 'empty':
            pass #_xml.raiseWrongXml(ctx, '', 'the component is already defined somewhere')
        descr.update(reader(ctx, subsection, descr['compactDescr'], unlocksDescrs, parentItem))
        descr['status'] = 'shared' #'local'
        res.append(descr)

    if not res:
        _xml.raiseWrongXml(xmlCtx, subsectionName, 'should be at least one subsection')
    return tuple(res)


def _readTags(xmlCtx, section, subsectionName, itemTypeName):
    # type: (tuple, object, str, str) -> frozenset
    """Read tag set from the given XML subsection.

    :param xmlCtx: parent XML context for error reporting.
    :param section: source XML section.
    :param subsectionName: subsection containing tag list.
    :param itemTypeName: vehicle component type name.
    :return: a frozenset of validated tag strings.
    """
    if itemTypeName != 'vehicle':
        tagNames = [] #_xml.readString(xmlCtx, section, subsectionName).split()
    else:
        tagNames = _xml.readString(xmlCtx, section, subsectionName).split()
    res = set()
    allowedTagNames = items.getTypeInfoByName(itemTypeName)['tags']
    for tagName in tagNames:
        if tagName not in allowedTagNames:
            _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown tag '%s'" % tagName)
        res.add(intern(tagName))

    return frozenset(res)


def _readLevel(xmlCtx, section):
    # type: (tuple, object) -> int
    """Read vehicle component level from XML.

    Validates that the level is within the expected range ``1..10``.

    :param xmlCtx: XML context for errors.
    :param section: XML section containing ``level`` tag.
    :return: integer level value.
    """
    level = section.readInt('level', 1)
    if not 1 <= level <= 10:
        _xml.raiseWrongSection(xmlCtx, 'level')
    return level


def _readIGRType(xmlCtx, section):
    # type: (tuple, object) -> int
    """Read IGR type value from XML section.

    :param xmlCtx: current XML context.
    :param section: source XML section.
    :return: integer value from :data:`IGR_TYPE` constants.
    """
    igrType = section.readInt('igrType', IGR_TYPE.NONE)
    if not IGR_TYPE.NONE <= igrType <= IGR_TYPE.PREMIUM:
        _xml.raiseWrongSection(xmlCtx, 'igrType')
    return igrType


def _readNations(xmlCtx, section):
    # type: (tuple, object) -> tuple or None
    """Return list of nation indices read from XML.

    :param xmlCtx: XML context for errors.
    :param section: section which may contain ``nations`` list.
    :return: tuple of nation indexes or ``None`` if subsection missing.
    """
    if not section.has_key('nations'):
        return
    else:
        values = section.readString('nations').split()
        result = []
        for nation in values:
            index = nations.INDICES.get(nation, None)
            if index is None:
                _xml.raiseWrongSection(xmlCtx, 'nations')
            result.append(index)

        return tuple(result)


def _readHull(xmlCtx, section):
    # type: (tuple, object) -> dict
    """Read hull descriptor from XML configuration.

    The hull is shared between multiple vehicle variants and includes
    information about models, hit testers and armor.

    :param xmlCtx: context for XML error reporting.
    :param section: XML section describing the hull.
    :return: dictionary with parsed parameters.
    """
    res = {'variantName': '',
     'hitTester': _readHitTester(xmlCtx, section, 'hitTester'),
     'materials': _readArmor(xmlCtx, section, 'armor'),
     'weight': _xml.readNonNegativeFloat(xmlCtx, section, 'weight'),
     'maxHealth': _xml.readInt(xmlCtx, section, 'maxHealth', 1),
     'ammoBayHealth': _readDeviceHealthParams(xmlCtx, section, 'ammoBayHealth', False)}
    if not IS_CLIENT or IS_DEVELOPMENT:
        res['armorHomogenization'] = 50.0 #_xml.readPositiveFloat(xmlCtx, section, 'armorHomogenization')
    v = []
    for s in _xml.getSubsection(xmlCtx, section, 'turretPositions').values():
        v.append(_xml.readVector3((xmlCtx, 'turretPositions'), s, ''))

    if not v:
        _xml.raiseWrongSection(xmlCtx, 'turretPositions')
    res['turretPositions'] = tuple(v)
    numTurrets = len(res['turretPositions'])
    if IS_CLIENT:
        res['turretHardPoints'] = __readTurretHardPoints(section, numTurrets)
    if numTurrets == 1:
        res['variantMatch'] = (None, None)
    else:
        res['variantMatch'] = (None,) * (1 + numTurrets)
    if not section.has_key('fakeTurrets'):
        res['fakeTurrets'] = _defFakeTurrets
    else:
        res['fakeTurrets'] = {'lobby': _readFakeTurretIndices(xmlCtx, section, 'fakeTurrets/lobby', numTurrets),
         'battle': _readFakeTurretIndices(xmlCtx, section, 'fakeTurrets/battle', numTurrets)}
    if IS_CLIENT:
        res['models'] = _readModels(xmlCtx, section, 'models')
        res['emblemSlots'] = _readEmblemSlots(xmlCtx, section, 'emblemSlots')
        res['swinging'] = {'lodDist': _readLodDist(xmlCtx, section, 'swinging/lodDist'),
         'sensitivityToImpulse': _xml.readNonNegativeFloat(xmlCtx, section, 'swinging/sensitivityToImpulse'),
         'pitchParams': _xml.readTupleOfFloats(xmlCtx, section, 'swinging/pitchParams', 6),
         'rollParams': _xml.readTupleOfFloats(xmlCtx, section, 'swinging/rollParams', 7)}
        res['exhaust'] = VehicleExhaustDescriptor(section, g_cache._exhaustEffects, xmlCtx)
        res['AODecals'] = _readAODecals(xmlCtx, section, 'AODecals')
        if section.has_key('camouflage'):
            res['camouflageTiling'], res['camouflageExclusionMask'] = _readCamouflageTilingAndMask(xmlCtx, section, 'camouflage', (None, None))
    if IS_CLIENT or IS_WEB or IS_CELLAPP:
        res['primaryArmor'] = _readPrimaryArmor(xmlCtx, section, 'primaryArmor', res['materials'])
    return res


_defFakeTurrets = {'lobby': (),
 'battle': ()}

def __readTurretHardPoints(section, numTurrets):
    # type: (object, int) -> tuple
    """Return tuple of turret joint nodes for the hull.

    When no explicit list is provided, a default joint name is repeated for
    ``numTurrets`` slots.

    :param section: hull XML section containing ``turretHardPoints``.
    :param numTurrets: expected number of turrets.
    :return: tuple with hard point identifiers.
    """
    thpSection = section['turretHardPoints']
    defaultJointHP = intern('HP_turretJoint')
    resultSeq = None
    if thpSection is None:
        resultSeq = (defaultJointHP for x in xrange(numTurrets))
    else:
        resultSeq = (intern(node.asString) for node in thpSection.values())
    result = tuple(resultSeq)
    assert len(result) == numTurrets
    return result


def _readHullVariants(xmlCtx, section, defHull, chassis, turrets):
    # type: (tuple, object, dict, tuple, tuple) -> tuple
    """Parse alternative hull variants from XML.

    Variants may override models or match specific chassis/turret combinations.

    :return: tuple of variant descriptor dictionaries.
    """
    res = []
    numTurrets = len(defHull['turretPositions'])
    for variantName, section in section.items():
        ctx = (xmlCtx, variantName)
        for prevVariant in res:
            if prevVariant['variantName'] == variantName:
                _xml.raiseWrongXml(xmlCtx, variantName, 'duplicate variant name')

        variantBase = defHull
        if section.has_key('base'):
            variantBaseName = section['base'].asString
            for prevVariant in res:
                if prevVariant['variantName'] == variantBaseName:
                    variantBase = prevVariant
                    break
            else:
                _xml.raiseWrongXml(ctx, 'base', 'unknown hull variant name "%s"' % variantBaseName)

        variant = variantBase.copy()
        variant['variantName'] = variantName
        variantMatch = variant['variantMatch'] = [None] * (1 + numTurrets)
        res.append(variant)
        isNonEmptyMatch = False
        for name in section.keys():
            if name == 'base':
                continue
            if name == 'models':
                variant['models'] = _readModels(ctx, section, 'models')
                continue
            if name == 'hitTester':
                variant['hitTester'] = _readHitTester(ctx, section, 'hitTester')
                continue
            if name == 'armor':
                variant['materials'] = _readArmor(ctx, section, 'armor')
                continue
            if name == 'weight':
                variant['weight'] = _xml.readNonNegativeFloat(ctx, section, 'weight')
                continue
            if name == 'turretPositions':
                v = []
                for s in _xml.getSubsection(ctx, section, 'turretPositions').values():
                    v.append(_xml.readVector3((ctx, 'turretPositions'), s, ''))

                if len(v) != numTurrets:
                    _xml.raiseWrongSection(ctx, 'turretPositions')
                variant['turretPositions'] = tuple(v)
                continue
            if name == 'turretHardPoints':
                if IS_CLIENT:
                    variant['turretHardPoints'] = __readTurretHardPoints(section, numTurrets)
                continue
            if name == 'emblemSlots':
                if IS_CLIENT:
                    variant['emblemSlots'] = _readEmblemSlots(xmlCtx, section, 'emblemSlots')
                continue
            if name == 'camouflage':
                if IS_CLIENT:
                    variant['camouflageTiling'], variant['camouflageExclusionMask'] = _readCamouflageTilingAndMask(xmlCtx, section, 'camouflage', (None, None))
                continue
            if name == 'chassis':
                if variantMatch[0] is not None:
                    _xml.raiseWrongXml(ctx, 'chassis', 'duplicate attr "chassis"')
                itemName = section['chassis'].asString
                for descr in chassis:
                    if descr['name'] == itemName:
                        variantMatch[0] = descr['id'][1]
                        isNonEmptyMatch = True
                        break
                else:
                    _xml.raiseWrongXml(ctx, 'chassis', 'unknown chassis "%s"' % itemName)

                continue
            if name.startswith('turret'):
                turretIndex = -1
                try:
                    turretIndex = int(name[len('turret'):])
                except:
                    pass

                if not 0 <= turretIndex < numTurrets:
                    _xml.raiseWrongXml(ctx, name, 'unsupported parameter')
                if variantMatch[1 + turretIndex] is not None:
                    _xml.raiseWrongXml(ctx, name, 'duplicate attr "%s"' % name)
                itemName = section[name].asString
                for descr in turrets[turretIndex]:
                    if descr['name'] == itemName:
                        variantMatch[1 + turretIndex] = descr['id'][1]
                        isNonEmptyMatch = True
                        break
                else:
                    _xml.raiseWrongXml(ctx, name, 'unknown turret "%s"' % itemName)

                continue
            _xml.raiseWrongXml(ctx, name, 'unsupported parameter')

        if not isNonEmptyMatch:
            _xml.raiseWrongXml(xmlCtx, variantName, 'no chassis or turret match specified')

    return tuple(res)


def _readChassis(xmlCtx, section, compactDescr, unlocksDescrs=None, parentItem=None):
    # type: (tuple, object, int, list or None, object or None) -> dict
    """Read a chassis descriptor.

    :param compactDescr: compact descriptor of the chassis.
    :param unlocksDescrs: list to collect unlock info, or ``None``.
    :param parentItem: optional parent descriptor used for context.
    :return: dictionary describing chassis parameters.
    """
    res = {'tags': _readTags(xmlCtx, section, 'tags', 'vehicleChassis'),
     'level': _readLevel(xmlCtx, section),
     'hullPosition': _xml.readVector3(xmlCtx, section, 'hullPosition'),
     'hitTester': _readHitTester(xmlCtx, section, 'hitTester'),
     'topRightCarryingPoint': _xml.readPositiveVector2(xmlCtx, section, 'topRightCarryingPoint'),
     'navmeshGirth': _xml.readPositiveFloat(xmlCtx, section, 'navmeshGirth'),
     'minPlaneNormalY': cos(radians(_xml.readPositiveFloat(xmlCtx, section, 'maxClimbAngle'))),
     'materials': _readArmor(xmlCtx, section, 'armor'),
     'weight': _xml.readPositiveFloat(xmlCtx, section, 'weight'),
     'maxLoad': _xml.readPositiveFloat(xmlCtx, section, 'maxLoad'),
     'specificFriction': _DEFAULT_SPECIFIC_FRICTION,
     'rotationSpeed': radians(_xml.readPositiveFloat(xmlCtx, section, 'rotationSpeed')),
     'rotationIsAroundCenter': _xml.readBool(xmlCtx, section, 'rotationIsAroundCenter')}
    if section.has_key('rotationSpeedLimit'):
        res['rotationSpeedLimit'] = radians(_xml.readPositiveFloat(xmlCtx, section, 'rotationSpeedLimit'))
    else:
        res['rotationSpeedLimit'] = None
    res['shotDispersionFactors'] = (_xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionFactors/vehicleMovement') / KMH_TO_MS, _xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionFactors/vehicleRotation') / radians(1.0))
    res['brakeForce'] = _xml.readPositiveFloat(xmlCtx, section, 'brakeForce') * 9.81
    v = _xml.readVector3(xmlCtx, section, 'terrainResistance').tuple()
    if not 0.0 < v[0] <= v[1] <= v[2]:
        _xml.raiseWrongSection(xmlCtx, 'terrainResistance')
    res['terrainResistance'] = v
    if not IS_CLIENT or IS_DEVELOPMENT:
        res['armorHomogenization'] = 1.0
        res['bulkHealthFactor'] = 1.0 #_xml.readPositiveFloat(xmlCtx, section, 'bulkHealthFactor')
    res.update(_readDeviceHealthParams(xmlCtx, section))
    if IS_CLIENT or IS_CELLAPP or IS_WEB:
        v = res['topRightCarryingPoint']
        topLeft = Vector2(-v.x, v.y)
        bottomLeft = Vector2(-v.x, -v.y)
        topRight = Vector2(v.x, v.y)
        bottomRight = Vector2(v.x, -v.y)
        res['carryingTriangles'] = (((topLeft + bottomLeft) / 2.0, topRight, bottomRight), ((topRight + bottomRight) / 2.0, bottomLeft, topLeft))
    if IS_CLIENT or IS_CELLAPP:
        wheelGroups = []
        wheels = []
        defSyncAngle = section.readFloat('wheels/leadingWheelSyncAngle', 60)
        for sname, subsection in _xml.getChildren(xmlCtx, section, 'wheels'):
            if sname == 'group':
                ctx = (xmlCtx, 'wheels/group')
                v = (_xml.readBool(ctx, subsection, 'isLeft'),
                 _xml.readNonEmptyString(ctx, subsection, 'template'),
                 _xml.readInt(ctx, subsection, 'count', 1),
                 subsection.readInt('startIndex', 0),
                 _xml.readPositiveFloat(ctx, subsection, 'radius'))
                wheelGroups.append(v)
            if sname == 'wheel':
                ctx = (xmlCtx, 'wheels/wheel')
                v = (_xml.readBool(ctx, subsection, 'isLeft'),
                 _xml.readNonEmptyString(ctx, subsection, 'name'),
                 _xml.readPositiveFloat(ctx, subsection, 'radius'),
                 subsection.readBool('isLeading', False),
                 subsection.readFloat('syncAngle', defSyncAngle))
                wheels.append(v)

        drivingWheelNames = section.readString('drivingWheels').split()
        if len(drivingWheelNames) != 2:
            _xml.raiseWrongSection(xmlCtx, 'drivingWheels')
        frontWheelSize = None
        rearWheelSize = None
        for _, wheelName, wheelRadius, _, _ in wheels:
            if wheelName == drivingWheelNames[0]:
                frontWheelSize = wheelRadius * 2.2
            if wheelName == drivingWheelNames[1]:
                rearWheelSize = wheelRadius * 2.2
            if frontWheelSize is not None and rearWheelSize is not None:
                break
        else:
            _xml.raiseWrongXml(xmlCtx, 'drivingWheels', 'unknown wheel name(s)')

        res['drivingWheelsSizes'] = (frontWheelSize, rearWheelSize)
    if IS_CLIENT:
        groundGroups = []
        groundNodes = []
        if section['groundNodes'] is not None:
            for sname, subsection in _xml.getChildren(xmlCtx, section, 'groundNodes'):
                if sname == 'group':
                    ctx = (xmlCtx, 'groundNodes/group')
                    v = (_xml.readBool(ctx, subsection, 'isLeft'),
                     _xml.readNonEmptyString(ctx, subsection, 'template'),
                     _xml.readInt(ctx, subsection, 'count', 1),
                     subsection.readInt('startIndex', 0),
                     _xml.readFloat(ctx, subsection, 'minOffset'),
                     _xml.readFloat(ctx, subsection, 'maxOffset'))
                    groundGroups.append(v)
                if sname == 'node':
                    ctx = (xmlCtx, 'groundNodes/node')
                    v = (_xml.readBool(ctx, subsection, 'isLeft'),
                     _xml.readNonEmptyString(ctx, subsection, 'name'),
                     _xml.readFloat(ctx, subsection, 'minOffset'),
                     _xml.readFloat(ctx, subsection, 'maxOffset'))
                    groundNodes.append(v)

        suspensionArms = []
        if section['suspension'] is not None:
            for sname, subsection in _xml.getChildren(xmlCtx, section, 'suspension'):
                ctx = (xmlCtx, 'suspension/arm')
                v = (_xml.readNonEmptyString(ctx, subsection, 'name'),
                 _xml.readFloat(ctx, subsection, 'minRoll'),
                 _xml.readFloat(ctx, subsection, 'maxRoll'),
                 _xml.readStringOrNone(ctx, subsection, 'child1'),
                 _xml.readStringOrNone(ctx, subsection, 'child2'),
                 _xml.readStringOrNone(ctx, subsection, 'childWheel1'),
                 _xml.readStringOrNone(ctx, subsection, 'childWheel2'))
                suspensionArms.append(v)

        trackGroups = []
        trackNodes = []
        trackParams = None
        if section['trackNodes'] is not None:
            trackParams = {'thickness': _xml.readFloat(ctx, section, 'trackThickness'),
             'maxAmplitude': _xml.readFloat(ctx, section, 'trackNodes/maxAmplitude'),
             'maxOffset': _xml.readFloat(ctx, section, 'trackNodes/maxOffset'),
             'gravity': _xml.readFloat(ctx, section, 'trackNodes/gravity')}
            defElasticity = section.readFloat('trackNodes/elasticity', 1500.0)
            defDamping = section.readFloat('trackNodes/damping', 1.0)
            defForwardElastK = section.readFloat('trackNodes/forwardElastK', 1.0)
            defBackwardElastK = section.readFloat('trackNodes/backwardElastK', 1.0)
            defOffset = section.readFloat('trackNodes/offset')
            for sname, subsection in _xml.getChildren(xmlCtx, section, 'trackNodes'):
                if sname == 'node':
                    ctx = (xmlCtx, 'trackNodes/node')
                    v = (_xml.readNonEmptyString(ctx, subsection, 'name'),
                     _xml.readBool(ctx, subsection, 'isLeft'),
                     subsection.readFloat('offset', defOffset),
                     subsection.readFloat('elasticity', defElasticity),
                     subsection.readFloat('damping', defDamping),
                     _xml.readStringOrNone(ctx, subsection, 'leftSibling'),
                     _xml.readStringOrNone(ctx, subsection, 'rightSibling'),
                     subsection.readFloat('forwardElastK', defForwardElastK),
                     subsection.readFloat('backwardElastK', defBackwardElastK))
                    trackNodes.append(v)

            ctx = (xmlCtx, 'trackNodes')
        if section['trackNodes'] is None and section['splineDesc'] is not None:
            trackParams = {'thickness': _xml.readFloat(ctx, section, 'trackThickness'),
             'maxAmplitude': 0.0,
             'maxOffset': 0.0,
             'elasticity': 1500.0,
             'damping': 0.0,
             'gravity': 0.0}
        splineDesc = None
        if section['splineDesc'] is not None:
            splineDesc = {'segmentModelLeft': _xml.readNonEmptyString(xmlCtx, section, 'splineDesc/segmentModelLeft'),
             'segmentModelRight': _xml.readNonEmptyString(xmlCtx, section, 'splineDesc/segmentModelRight'),
             'segmentLength': _xml.readFloat(xmlCtx, section, 'splineDesc/segmentLength'),
             'leftDesc': _xml.readStringOrNone(xmlCtx, section, 'splineDesc/left'),
             'rightDesc': _xml.readStringOrNone(xmlCtx, section, 'splineDesc/right'),
             'lodDist': _readLodDist(xmlCtx, section, 'splineDesc/lodDist'),
             'segmentOffset': section.readFloat('splineDesc/segmentOffset', 0),
             'segment2ModelLeft': _xml.readStringOrNone(xmlCtx, section, 'splineDesc/segment2ModelLeft'),
             'segment2ModelRight': _xml.readStringOrNone(xmlCtx, section, 'splineDesc/segment2ModelRight'),
             'segment2Offset': section.readFloat('splineDesc/segment2Offset', 0),
             'atlasUTiles': section.readInt('splineDesc/atlas/UTiles', 1),
             'atlasVTiles': section.readInt('splineDesc/atlas/VTiles', 1)}
        if section.has_key('camouflage'):
            res['camouflageTiling'], res['camouflageExclusionMask'] = _readCamouflageTilingAndMask(xmlCtx, section, 'camouflage', (None, None))
    _readPriceForItem(xmlCtx, section, compactDescr)
    if IS_CLIENT or IS_WEB:
        _readUserText(res, section)
    if IS_CLIENT:
        res['models'] = _readModels(xmlCtx, section, 'models')
        res['traces'] = {'lodDist': _readLodDist(xmlCtx, section, 'traces/lodDist'),
         'bufferPrefs': _xml.readNonEmptyString(xmlCtx, section, 'traces/bufferPrefs'),
         'textureSet': _xml.readNonEmptyString(xmlCtx, section, 'traces/textureSet'),
         'centerOffset': res['topRightCarryingPoint'][0],
         'size': _xml.readPositiveVector2(xmlCtx, section, 'traces/size')}
        res['tracks'] = {'lodDist': _readLodDist(xmlCtx, section, 'tracks/lodDist'),
         'leftMaterial': _xml.readNonEmptyString(xmlCtx, section, 'tracks/leftMaterial'),
         'rightMaterial': _xml.readNonEmptyString(xmlCtx, section, 'tracks/rightMaterial'),
         'textureScale': _xml.readFloat(xmlCtx, section, 'tracks/textureScale')}
        res['wheels'] = {'lodDist': _readLodDist(xmlCtx, section, 'wheels/lodDist'),
         'leadingWheelSyncAngle': section.readFloat('wheels/leadingWheelSyncAngle', 60)}
        res['groundNodes'] = {'groups': groundGroups,
         'nodes': groundNodes}
        res['suspensionArms'] = suspensionArms
        res['trackNodes'] = {'groups': trackGroups,
         'nodes': trackNodes}
        res['trackParams'] = trackParams
        res['splineDesc'] = splineDesc
        res['effects'] = {'lodDist': _readLodDist(xmlCtx, section, 'effects/lodDist'),
         'dust': _readChassisEffects(xmlCtx, section, 'effects/dust'),
         'mud': _readChassisEffects(xmlCtx, section, 'effects/mud')}
        res['sound'] = section.readString('sound', '')
        res['soundPC'] = section.readString('soundPC', '')
        res['soundNPC'] = section.readString('soundNPC', '')
        if res['sound'] == '' and (res['soundPC'] == '' or res['soundNPC'] == ''):
            raise Exception, 'chassis sound tags are wrong for vehicle ' + res['userString']
        res['wheels']['groups'] = wheelGroups
        res['wheels']['wheels'] = wheels
        res['AODecals'] = _readAODecals(xmlCtx, section, 'AODecals')
    res['unlocks'] = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, compactDescr)
    return res


def _readChassisLocals(xmlCtx, section, sharedDescr, unlocksDescrs, parentItem=None):
    # type: (tuple, object, dict, list, object or None) -> dict
    """Parse local chassis overrides for a specific vehicle.

    When no parameters are overridden the shared descriptor is returned
    unchanged.

    :return: chassis descriptor dictionary.
    """
    hasOverride = False
    if IS_CLIENT:
        sharedCam = (sharedDescr.get('camouflageTiling'), sharedDescr.get('camouflageExclusionMask'))
        cam = _readCamouflageTilingAndMask(xmlCtx, section, 'camouflage', sharedCam)
        if cam != sharedCam:
            hasOverride = True
    if not section.has_key('unlocks'):
        unlocks = sharedDescr['unlocks']
    else:
        hasOverride = True
        unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, sharedDescr['compactDescr'])
    if not hasOverride:
        return sharedDescr
    descr = sharedDescr.copy()
    descr['unlocks'] = unlocks
    if IS_CLIENT:
        descr['camouflageTiling'] = cam[0]
        descr['camouflageExclusionMask'] = cam[1]
    return descr


def _readEngine(xmlCtx, section, compactDescr, unlocksDescrs=None, parentItem=None):
    # type: (tuple, object, int, list or None, object or None) -> dict
    """Read engine parameters for a vehicle.

    :param compactDescr: compact descriptor of this engine.
    :return: dictionary describing engine characteristics.
    """
    res = {'tags': _readTags(xmlCtx, section, 'tags', 'vehicleEngine'),
     'level': _readLevel(xmlCtx, section),
     'power': 550.0, #_xml.readPositiveFloat(xmlCtx, section, 'power') * HP_TO_WATTS,
     'weight': 20.0, #_xml.readPositiveFloat(xmlCtxEngines, section, 'weight'),
     'fireStartingChance': 2.0, #_xml.readFraction(xmlCtxEngines, section, 'fireStartingChance'),
     'minFireStartingDamage': 20.0} #g_cache.commonConfig['miscParams']['minFireStartingDamage']}
    _readPriceForItem(xmlCtx, section, compactDescr)
    if IS_CLIENT or IS_WEB:
        _readUserText(res, section)
    if IS_CLIENT:
        res['sound'] = section.readString('sound', '')
        res['soundPC'] = section.readString('soundPC', '')
        res['soundNPC'] = section.readString('soundNPC', '')
        if res['sound'] == '' and (res['soundPC'] == '' or res['soundNPC'] == ''):
            LOG_DEBUG('sound, soundPC, soundNPC', res['sound'], res['soundPC'], res['soundNPC'])
            _xml.raiseWrongXml(xmlCtx, '', 'chassis sound tags are wrong')
    res.update(_readDeviceHealthParams(xmlCtx, section))
    res['unlocks'] = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, compactDescr)
    return res


def _readFuelTank(xmlCtx, section, compactDescr, unlocksDescrs=None, parentItem=None):
    # type: (tuple, object, int, list or None, object or None) -> dict
    """Read fuel tank descriptor from XML."""
    res = {'tags': _readTags(xmlCtx, section, 'tags', 'vehicleEngine'),
     'level': _readLevel(xmlCtx, section),
     'weight': 20} #_xml.readPositiveFloat(xmlCtx, section, 'weight')}
    _readPriceForItem(xmlCtx, section, compactDescr)
    if IS_CLIENT or IS_WEB:
        _readUserText(res, section)
    res.update(_readDeviceHealthParams(xmlCtx, section, '', False))
    res['unlocks'] = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, compactDescr)
    return res


def _readRadio(xmlCtx, section, compactDescr, unlocksDescrs=None, parentItem=None):
    # type: (tuple, object, int, list or None, object or None) -> dict
    """Read radio parameters from XML."""
    res = {'tags': _readTags(xmlCtx, section, 'tags', 'vehicleEngine'),
     'level': _readLevel(xmlCtx, section),
     'weight': 20, #_xml.readNonNegativeFloat(xmlCtx, section, 'weight'),
     'distance': 750} #_xml.readNonNegativeFloat(xmlCtx, section, 'distance')}
    _readPriceForItem(xmlCtx, section, compactDescr)
    if IS_CLIENT or IS_WEB:
        _readUserText(res, section)
    res.update(_readDeviceHealthParams(xmlCtx, section))
    res['unlocks'] = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, compactDescr)
    return res


def _readTurret(xmlCtx, section, compactDescr, unlocksDescrs=None, parentItem=None):
    # type: (tuple, object, int, list or None, object or None) -> dict
    """Read turret descriptor including guns list."""
    res = {'tags': _readTags(xmlCtx, section, 'tags', 'vehicleTurret'),
     'level': _readLevel(xmlCtx, section),
     'hitTester': _readHitTester(xmlCtx, section, 'hitTester'),
     'gunPosition': _xml.readVector3(xmlCtx, section, 'gunPosition'),
     'materials': _readArmor(xmlCtx, section, 'armor'),
     'weight': _xml.readNonNegativeFloat(xmlCtx, section, 'weight'),
     'maxHealth': _xml.readInt(xmlCtx, section, 'maxHealth', 1),
     'rotationSpeed': radians(_xml.readPositiveFloat(xmlCtx, section, 'rotationSpeed')),
     'turretRotatorHealth': _readDeviceHealthParams(xmlCtx, section, 'turretRotatorHealth'),
     'surveyingDeviceHealth': _readDeviceHealthParams(xmlCtx, section, 'surveyingDeviceHealth')}
    if not IS_CLIENT or IS_DEVELOPMENT:
        res['armorHomogenization'] = 1.0 #_xml.readPositiveFloat(xmlCtx, section, 'armorHomogenization')
        if section.has_key('invisibilityFactor'):
            res['invisibilityFactor'] = _xml.readNonNegativeFloat(xmlCtx, section, 'invisibilityFactor')
        else:
            res['invisibilityFactor'] = 1.0
    _readPriceForItem(xmlCtx, section, compactDescr)
    if IS_CLIENT or IS_WEB:
        _readUserText(res, section)
    if IS_CLIENT or IS_WEB or IS_CELLAPP:
        res['primaryArmor'] = _readPrimaryArmor(xmlCtx, section, 'primaryArmor', res['materials'])
    if IS_CLIENT:
        res['ceilless'] = section.readBool('ceilless', False)
        res['models'] = _readModels(xmlCtx, section, 'models')
        res['showEmblemsOnGun'] = section.readBool('showEmblemsOnGun', False)
        res['emblemSlots'] = _readEmblemSlots(xmlCtx, section, 'emblemSlots')
        if section.has_key('camouflage'):
            res['camouflageTiling'], res['camouflageExclusionMask'] = _readCamouflageTilingAndMask(xmlCtx, section, 'camouflage', (None, None))
        res['turretRotatorSoundManual'] = section.readString('turretRotatorSoundManual')
        res['turretRotatorSoundGear'] = section.readString('turretRotatorSoundGear')
        res['AODecals'] = _readAODecals(xmlCtx, section, 'AODecals')
        commonConfig = g_cache.commonConfig
        res['turretDetachmentEffects'] = _readTurretDetachmentEffects(xmlCtx, section, 'turretDetachmentEffects', commonConfig['defaultTurretDetachmentEffects'])
    if IS_CELLAPP:
        arrayStr = section.readString('physicsShape')
        strArr = arrayStr.split()
        res['physicsShape'] = tuple(map(float, strArr))
    v = _xml.readNonNegativeFloat(xmlCtx, section, 'circularVisionRadius')
    res['circularVisionRadius'] = v
    nationID = parseIntCompactDescr(compactDescr)[1]
    res['guns'] = _readInstallableComponents(xmlCtx, section, 'guns', nationID, _readGun, _readGunLocals, g_cache.guns(nationID), g_cache.gunIDs(nationID), unlocksDescrs, compactDescr)
    res['unlocks'] = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, compactDescr)
    return res


def _readTurretLocals(xmlCtx, section, sharedDescr, unlocksDescrs, parentItem=None):
    # type: (tuple, object, dict, list, object or None) -> dict
    """Read turret parameters overridden for a specific vehicle."""
    hasOverride = False
    nationID = sharedDescr['id'][0]
    if not section.has_key('guns'):
        guns = sharedDescr['guns']
    else:
        hasOverride = True
        guns = _readInstallableComponents(xmlCtx, section, 'guns', nationID, _readGun, _readGunLocals, g_cache.guns(nationID), g_cache.gunIDs(nationID), unlocksDescrs, sharedDescr['compactDescr'])
    if IS_CLIENT:
        sharedCam = (sharedDescr.get('camouflageTiling'), sharedDescr.get('camouflageExclusionMask'))
        cam = _readCamouflageTilingAndMask(xmlCtx, section, 'camouflage', sharedCam)
        if cam != sharedCam:
            hasOverride = True
    if not section.has_key('unlocks'):
        unlocks = sharedDescr['unlocks']
    else:
        hasOverride = True
        unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, sharedDescr['compactDescr'])
    if not hasOverride:
        return sharedDescr
    descr = sharedDescr.copy()
    descr['guns'] = guns
    descr['unlocks'] = unlocks
    if IS_CLIENT:
        descr['camouflageTiling'] = cam[0]
        descr['camouflageExclusionMask'] = cam[1]
    return descr


def _readGun(xmlCtx, section, compactDescr, unlocksDescrs=None, turretCompactDescr=None):
    # type: (tuple, object, int, list or None, int or None) -> dict
    """Read gun descriptor from XML."""
    nationID, gunID = parseIntCompactDescr(compactDescr)[1:3]
    
    if not section.has_key('rotationSpeed') or not section.has_key('weight'):
        gunName = section.name
        nationName = nations.NAMES[nationID]
        gunsPath = _VEHICLE_TYPE_XML_PATH + nationName + '/components/guns.xml'
        gunsSection = ResMgr.openSection(gunsPath)
        if gunsSection is None:
            _xml.raiseWrongXml(None, gunsPath, 'can not open or read')
        sharedSec = _xml.getSubsection((None, gunsPath), gunsSection, 'shared')
        gunSec = sharedSec[gunName]
        if gunSec is None:
            _xml.raiseWrongXml(xmlCtx, 'gunSec', 'no gun exists')
        gunCtx = (None, gunsPath + '/shared/' + gunName)
        res = {
            'tags': _readTags(xmlCtx, section, 'tags', 'vehicleGun'),
            'level': _readLevel(xmlCtx, section),
            'rotationSpeed': _xml.readPositiveFloat(gunCtx, gunSec, 'rotationSpeed'), #radians(20.0)
            'weight': _xml.readPositiveFloat(gunCtx, gunSec, 'weight'), #20
            'reloadTime': _xml.readPositiveFloat(gunCtx, gunSec, 'reloadTime'), #12.0
            'aimingTime': _xml.readPositiveFloat(gunCtx, gunSec, 'aimingTime'), #2.0
            'maxAmmo': _xml.readInt(gunCtx, gunSec, 'maxAmmo', 1) #23???
        }
        gunsSection = None
        ResMgr.purge(gunsPath, True)
    else:
        res = {
            'tags': _readTags(xmlCtx, section, 'tags', 'vehicleGun'),
            'level': _readLevel(xmlCtx, section),
            'rotationSpeed': _xml.readPositiveFloat(xmlCtx, section, 'rotationSpeed'), #radians(20.0)
            'weight': _xml.readPositiveFloat(xmlCtx, section, 'weight'), #20
            'reloadTime': _xml.readPositiveFloat(xmlCtx, section, 'reloadTime'), #12.0
            'aimingTime': _xml.readPositiveFloat(xmlCtx, section, 'aimingTime'), #2.0
            'maxAmmo': _xml.readInt(xmlCtx, section, 'maxAmmo', 1) #23???
        }
    if not IS_CLIENT or IS_DEVELOPMENT:
        res['invisibilityFactorAtShot'] = 1.0 #_xml.readFraction(xmlCtx, section, 'invisibilityFactorAtShot')
        res['armorHomogenization'] = 1.0
    _readPriceForItem(xmlCtx, section, compactDescr)
    if IS_CLIENT or IS_WEB:
        _readUserText(res, section)
    if IS_CLIENT:
        if section.has_key('models'):
            res['models'] = _readModels(xmlCtx, section, 'models')
        else:
            res['models'] = None
        effName = _xml.readNonEmptyString(xmlCtx, section, 'effects')
        eff = g_cache._gunEffects.get(effName)
        if eff is None:
            _xml.raiseWrongXml(xmlCtx, 'effects', "unknown effect '%s'" % effName)
        res['effects'] = eff
        res['impulse'] = _xml.readNonNegativeFloat(xmlCtx, section, 'impulse')
        res['recoil'] = {'lodDist': _readLodDist(xmlCtx, section, 'recoil/lodDist'),
         'amplitude': _xml.readNonNegativeFloat(xmlCtx, section, 'recoil/amplitude'),
         'backoffTime': _xml.readNonNegativeFloat(xmlCtx, section, 'recoil/backoffTime'),
         'returnTime': _xml.readNonNegativeFloat(xmlCtx, section, 'recoil/returnTime')}
        if section.has_key('camouflage'):
            res['camouflageTiling'], res['camouflageExclusionMask'] = _readCamouflageTilingAndMask(xmlCtx, section, 'camouflage', (None, None))
        res['animateEmblemSlots'] = section.readBool('animateEmblemSlots', True)
        if section.has_key('emblemSlots'):
            res['emblemSlots'] = _readEmblemSlots(xmlCtx, section, 'emblemSlots')
        else:
            res['emblemSlots'] = ()
    if section.has_key('hitTester'):
        res['hitTester'] = _readHitTester(xmlCtx, section, 'hitTester')
    else:
        res['hitTester'] = None
    if section.has_key('armor'):
        res['materials'] = _readArmor(xmlCtx, section, 'armor')
    else:
        res['materials'] = None
    if not IS_BASEAPP: #not section.has_key('turretYawLimits'):
        _xml.raiseWrongSection(xmlCtx, 'turretYawLimits')
    else:
        v = (-10, 150) #_xml.readVector2(xmlCtx, section, 'turretYawLimits')
        if v[0] > v[1]:
            _xml.raiseWrongSection(xmlCtx, 'turretYawLimits')
        v = (radians(v[0]), radians(v[1])) if v[0] > -179.0 or v[1] < 179.0 else None
        res['turretYawLimits'] = v
    if not IS_BASEAPP: #not section.has_key('pitchLimits'):
        _xml.raiseWrongSection(xmlCtx, 'pitchLimits')
    else:
        v = (-10, 150) #_xml.readVector2(xmlCtx, section, 'pitchLimits')
        if v[0] > v[1]:
            _xml.raiseWrongSection(xmlCtx, 'pitchLimits')
        basicLimits = (radians(v[0]), radians(v[1]))
        pitchLimits = {'basic': basicLimits,
         'absolute': basicLimits}
        if section.has_key('extraPitchLimits'):
            _readGunPitchExtraLimits((xmlCtx, 'extraPitchLimits'), section['extraPitchLimits'], pitchLimits)
        res['pitchLimits'] = pitchLimits
    res.update(_readDeviceHealthParams(xmlCtx, section))
    res['shotDispersionAngle'] = atan(20.0 / 100.0) #_xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionRadius') / 100.0)
    res['shotDispersionFactors'] = _readGunShotDispersionFactors(xmlCtx, section, 'shotDispersionFactors')
    if not section.has_key('burst'):
        res['burst'] = (1, 0.0)
    else:
        res['burst'] = _readGunClipBurst(xmlCtx, section, 'burst')
    if not section.has_key('clip'):
        res['clip'] = (1, 0.0)
    else:
        res['clip'] = _readGunClipBurst(xmlCtx, section, 'clip')
    if res['burst'][0] > res['clip'][0] > 1:
        _xml.raiseWrongXml(xmlCtx, 'burst', 'burst/count is larger than clip/count')
    tags = res['tags']
    if res['clip'][0] == 1:
        tags = tags.difference(('clip',))
    else:
        tags = tags.union(('clip',))
    res['tags'] = tags
    v = []
    projSpeedFactor = g_cache.commonConfig['miscParams']['projectileSpeedFactor']
    if section.has_key('shots'):
        for sname, subsection in _xml.getChildren(xmlCtx, section, 'shots'):
            v.append(_readShot((xmlCtx, 'shots/' + sname), subsection, nationID, projSpeedFactor))
        if not v:
            _xml.raiseWrongXml(xmlCtx, 'shots', 'no shots are specified')
    else:
        gunName = section.name
        nationName = nations.NAMES[nationID]
        gunsPath = _VEHICLE_TYPE_XML_PATH + nationName + '/components/guns.xml'
        gunsSection = ResMgr.openSection(gunsPath)
        if gunsSection is None:
            _xml.raiseWrongXml(None, gunsPath, 'can not open or read')
        sharedSec = _xml.getSubsection((None, gunsPath), gunsSection, 'shared')
        gunSec = sharedSec[gunName]
        if gunSec is None:
            _xml.raiseWrongXml(xmlCtx, 'shots', 'no shots are specified')
        if gunSec.has_key('shots'):
            for sname, subsection in _xml.getChildren((None, gunsPath + '/shared/' + gunName), gunSec, 'shots'):
                v.append(_readShot((xmlCtx, 'shots/' + sname), subsection, nationID, projSpeedFactor))
        gunsSection = None
        ResMgr.purge(gunsPath, True)
        if not v:
            _xml.raiseWrongXml(xmlCtx, 'shots', 'no shots are specified')
    if not v:
        _xml.raiseWrongXml(xmlCtx, 'shots', 'no shots are specified')
    res['shots'] = tuple(v)
    res['unlocks'] = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, compactDescr)
    return res


def _readGunLocals(xmlCtx, section, sharedDescr, unlocksDescrs, turretCompactDescr):
    # type: (tuple, object, dict, list, int) -> dict
    """Read gun overrides relative to the shared descriptor."""
    hasOverride = False
    if not section.has_key('turretYawLimits'):
        turretYawLimits = sharedDescr['turretYawLimits']
    else:
        hasOverride = True
        v = _xml.readVector2(xmlCtx, section, 'turretYawLimits')
        if v[0] > v[1]:
            _xml.raiseWrongSection(xmlCtx, 'turretYawLimits')
        turretYawLimits = (radians(v[0]), radians(v[1])) if v[0] > -179.0 or v[1] < 179.0 else None
    if section.has_key('pitchLimits'):
        hasOverride = True
        v = _xml.readVector2(xmlCtx, section, 'pitchLimits')
        if v[0] > v[1]:
            _xml.raiseWrongSection(xmlCtx, 'pitchLimits')
        basicLimits = (radians(v[0]), radians(v[1]))
        pitchLimits = {'basic': basicLimits,
         'absolute': basicLimits}
    else:
        pitchLimits = dict(sharedDescr['pitchLimits'])
    if section.has_key('extraPitchLimits'):
        hasOverride = True
        _readGunPitchExtraLimits((xmlCtx, 'extraPitchLimits'), section['extraPitchLimits'], pitchLimits)
    if not section.has_key('rotationSpeed'):
        rotationSpeed = sharedDescr['rotationSpeed']
    else:
        hasOverride = True
        rotationSpeed = radians(_xml.readPositiveFloat(xmlCtx, section, 'rotationSpeed'))
    if not section.has_key('reloadTime'):
        reloadTime = sharedDescr['reloadTime']
    else:
        hasOverride = True
        reloadTime = _xml.readPositiveFloat(xmlCtx, section, 'reloadTime')
    if not section.has_key('aimingTime'):
        aimingTime = sharedDescr['aimingTime']
    else:
        hasOverride = True
        aimingTime = _xml.readPositiveFloat(xmlCtx, section, 'aimingTime')
    if not section.has_key('maxAmmo'):
        ammo = sharedDescr['maxAmmo']
    else:
        hasOverride = True
        ammo = _xml.readInt(xmlCtx, section, 'maxAmmo', 1)
    if not section.has_key('shotDispersionRadius'):
        shotDispAngle = sharedDescr['shotDispersionAngle']
    else:
        hasOverride = True
        shotDispAngle = _xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionRadius') / 100.0
    if not section.has_key('shotDispersionFactors'):
        shotDispFactors = sharedDescr['shotDispersionFactors']
    else:
        hasOverride = True
        shotDispFactors = _readGunShotDispersionFactors(xmlCtx, section, 'shotDispersionFactors')
    if not section.has_key('burst'):
        burst = sharedDescr['burst']
    else:
        hasOverride = True
        burst = _readGunClipBurst(xmlCtx, section, 'burst')
    if not section.has_key('clip'):
        clip = sharedDescr['clip']
    else:
        hasOverride = True
        clip = _readGunClipBurst(xmlCtx, section, 'clip')
    if burst[0] > clip[0] > 1:
        _xml.raiseWrongXml(xmlCtx, 'burst', 'burst/count is larger than clip/count')
    if not IS_CLIENT or IS_DEVELOPMENT:
        if not section.has_key('invisibilityFactorAtShot'):
            invisibilityFactorAtShot = 1.0 #sharedDescr['invisibilityFactorAtShot']
        else:
            hasOverride = True
            invisibilityFactorAtShot = _xml.readFraction(xmlCtx, section, 'invisibilityFactorAtShot')
    if IS_CLIENT:
        if not section.has_key('models'):
            models = sharedDescr['models']
            if models is None:
                _xml.raiseWrongSection(xmlCtx, 'models')
        else:
            hasOverride = True
            models = _readModels(xmlCtx, section, 'models')
        if not section.has_key('effects'):
            effects = sharedDescr['effects']
        else:
            hasOverride = True
            effName = _xml.readNonEmptyString(xmlCtx, section, 'effects')
            effects = g_cache._gunEffects.get(effName)
            if effects is None:
                _xml.raiseWrongXml(xmlCtx, 'effects', "unknown effect '%s'" % effName)
        if not section.has_key('recoil'):
            recoil = sharedDescr['recoil']
        else:
            hasOverride = True
            recoil = {'lodDist': _readLodDist(xmlCtx, section, 'recoil/lodDist'),
             'amplitude': _xml.readNonNegativeFloat(xmlCtx, section, 'recoil/amplitude'),
             'backoffTime': _xml.readNonNegativeFloat(xmlCtx, section, 'recoil/backoffTime'),
             'returnTime': _xml.readNonNegativeFloat(xmlCtx, section, 'recoil/returnTime')}
        sharedCam = (sharedDescr.get('camouflageTiling'), sharedDescr.get('camouflageExclusionMask'))
        cam = _readCamouflageTilingAndMask(xmlCtx, section, 'camouflage', sharedCam)
        if cam != sharedCam:
            hasOverride = True
        if not section.has_key('animateEmblemSlots'):
            animateEmblemSlots = sharedDescr['animateEmblemSlots']
        else:
            hasOverride = True
            animateEmblemSlots = section.readBool('animateEmblemSlots', True)
        if not section.has_key('emblemSlots'):
            emblemSlots = sharedDescr['emblemSlots']
        else:
            hasOverride = True
            emblemSlots = _readEmblemSlots(xmlCtx, section, 'emblemSlots')
    if IS_BASEAPP:
        hitTester = None
        materials = None
    else:
        if not section.has_key('hitTester'):
            hitTester = sharedDescr['hitTester']
            if hitTester is None:
                _xml.raiseWrongSection(xmlCtx, 'hitTester')
        else:
            hasOverride = True
            hitTester = _readHitTester(xmlCtx, section, 'hitTester')
        if not section.has_key('armor'):
            materials = sharedDescr['materials']
            if materials is None:
                _xml.raiseWrongSection(xmlCtx, 'armor')
        else:
            hasOverride = True
            materials = _readArmor(xmlCtx, section, 'armor')
    if not section.has_key('unlocks'):
        unlocks = sharedDescr['unlocks']
    else:
        hasOverride = True
        unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, sharedDescr['compactDescr'], turretCompactDescr)
    if not hasOverride:
        return sharedDescr
    else:
        descr = sharedDescr.copy()
        descr['turretYawLimits'] = turretYawLimits
        descr['pitchLimits'] = pitchLimits
        descr['rotationSpeed'] = rotationSpeed
        descr['reloadTime'] = reloadTime
        descr['aimingTime'] = aimingTime
        descr['maxAmmo'] = ammo
        descr['shotDispersionAngle'] = shotDispAngle
        descr['shotDispersionFactors'] = shotDispFactors
        descr['burst'] = burst
        descr['unlocks'] = unlocks
        descr['hitTester'] = hitTester
        descr['materials'] = materials
        if clip is not sharedDescr['clip']:
            descr['clip'] = clip
            tags = descr['tags']
            if clip[0] == 1:
                tags = tags.difference(('clip',))
            else:
                tags = tags.union(('clip',))
            descr['tags'] = tags
        if IS_CLIENT:
            descr['models'] = models
            descr['effects'] = effects
            descr['recoil'] = recoil
            descr['camouflageTiling'] = cam[0]
            descr['camouflageExclusionMask'] = cam[1]
            descr['animateEmblemSlots'] = animateEmblemSlots
            descr['emblemSlots'] = emblemSlots
        if not IS_CLIENT or IS_DEVELOPMENT:
            descr['invisibilityFactorAtShot'] = invisibilityFactorAtShot
        return descr


def _readGunClipBurst(xmlCtx, section, type):
    # type: (tuple, object, str) -> tuple
    """Read gun burst or clip definition."""
    count = _xml.readInt(xmlCtx, section, type + '/count', 1)
    interval = 60.0 / _xml.readPositiveFloat(xmlCtx, section, type + '/rate')
    return (count, interval if count > 1 else 0.0)


def _readGunPitchExtraLimits(xmlCtx, section, descToUpdate):
    # type: (tuple, object, dict) -> bool
    """Read extra gun pitch limit sections.

    :return: ``True`` if any limits were read.
    """
    readSomething = False
    extraAngle = 0.0
    if section.has_key('front'):
        v = _xml.readVector3(xmlCtx, section, 'front')
        if v[0] > v[1]:
            _xml.raiseWrongSection(xmlCtx, 'front')
        descToUpdate['front'] = tuple((radians(ang) for ang in v))
        descToUpdate['absolute'] = (min(descToUpdate['absolute'][0], descToUpdate['front'][0]), max(descToUpdate['absolute'][1], descToUpdate['front'][1]))
        extraAngle += descToUpdate['front'][2]
        readSomething = True
    if section.has_key('back'):
        v = _xml.readVector3(xmlCtx, section, 'back')
        if v[0] > v[1]:
            _xml.raiseWrongSection(xmlCtx, 'back')
        descToUpdate['back'] = tuple((radians(ang) for ang in v))
        descToUpdate['absolute'] = (min(descToUpdate['absolute'][0], descToUpdate['back'][0]), max(descToUpdate['absolute'][1], descToUpdate['back'][1]))
        extraAngle += descToUpdate['back'][2]
        readSomething = True
    if section.has_key('transition'):
        v = _xml.readFloat(xmlCtx, section, 'transition')
        descToUpdate['transition'] = radians(v)
        extraAngle += descToUpdate['transition'] * 4.0
        readSomething = True
    else:
        extraAngle += DEFAULT_GUN_PITCH_LIMITS_TRANSITION * 4.0
    if extraAngle > pi * 2.0:
        _xml.raiseWrongXml(xmlCtx[0], xmlCtx[1], 'overlapping sectors')
    return readSomething


def _readShells(xmlPath, nationID):
    # type: (str, int) -> tuple
    """Load shell definitions for given nation."""
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    icons = {}
    if IS_CLIENT or IS_WEB:
        for name, subsection in _xml.getChildren((None, xmlPath), section, 'icons'):
            name = intern(name)
            if icons.has_key(name):
                _xml.raiseWrongXml((None, xmlPath + '/icons'), name, 'name is not unique')
            icons[name] = _xml.readIcon((None, xmlPath + '/icons'), subsection, '')

    descrs = {}
    ids = {}
    for name, subsection in section.items():
        if name == 'icons':
            continue
        xmlCtx = (None, xmlPath + '/' + name)
        name = intern(name)
        if ids.has_key(name):
            _xml.raiseWrongXml(xmlCtx, '', 'shell type name is not unique')
        id = _xml.readInt(xmlCtx, subsection, 'id', 0, 65535)
        if descrs.has_key(id):
            _xml.raiseWrongXml(xmlCtx, 'id', 'shell type ID is not unique')
        descrs[id] = _readShell(xmlCtx, subsection, name, nationID, id, icons)
        ids[name] = id

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return (descrs, ids)


def _readShell(xmlCtx, section, name, nationID, shellTypeID, icons):
    # type: (tuple, object, str, int, int, dict) -> dict
    """Parse single shell description."""
    compactDescr = makeIntCompactDescrByID('shell', nationID, shellTypeID)
    res = {'itemTypeName': 'shell',
     'name': name,
     'id': (nationID, shellTypeID),
     'compactDescr': compactDescr,
     'caliber': _xml.readPositiveFloat(xmlCtx, section, 'caliber'),
     'isTracer': section.readBool('isTracer', False),
     'damage': (_xml.readPositiveFloat(xmlCtx, section, 'damage/armor'), _xml.readPositiveFloat(xmlCtx, section, 'damage/devices')),
     'damageRandomization': 0.25,
     'piercingPowerRandomization': 0.25}
    if IS_CLIENT or IS_WEB:
        res['userString'] = i18n.makeString(section.readString('userString'))
        res['description'] = i18n.makeString(section.readString('description'))
        v = _xml.readNonEmptyString(xmlCtx, section, 'icon')
        res['icon'] = icons.get(v)
        if res['icon'] is None:
            _xml.raiseWrongXml(xmlCtx, 'icon', "unknown icon '%s'" % v)
    _readPriceForItem(xmlCtx, section, compactDescr)
    kind = intern(_xml.readNonEmptyString(xmlCtx, section, 'kind'))
    if kind not in _shellKinds:
        _xml.raiseWrongXml(xmlCtx, 'kind', "unknown shell kind '%s'" % kind)
    res['kind'] = kind
    if not IS_CLIENT or IS_DEVELOPMENT:
        if kind.startswith('ARMOR_PIERCING'):
            res['normalizationAngle'] = radians(10.0) #_xml.readNonNegativeFloat(xmlCtx, section, 'normalizationAngle'))
            res['ricochetAngleCos'] = cos(radians(10.0)) #_xml.readNonNegativeFloat(xmlCtx, section, 'ricochetAngle')))
        elif kind == 'HOLLOW_CHARGE':
            res['piercingPowerLossFactorByDistance'] = 10.0 # * _xml.readNonNegativeFloat(xmlCtx, section, 'piercingPowerLossFactorByDistance')
            res['ricochetAngleCos'] = cos(radians(10.0)) #_xml.readNonNegativeFloat(xmlCtx, section, 'ricochetAngle')))
    if kind == 'HIGH_EXPLOSIVE':
        res['explosionRadius'] = section.readFloat('explosionRadius')
        if res['explosionRadius'] <= 0.0:
            res['explosionRadius'] = res['caliber'] * res['caliber'] / 5555.0
    effName = _xml.readNonEmptyString(xmlCtx, section, 'effects')
    v = g_cache.shotEffectsIndexes.get(effName)
    if v is None:
        _xml.raiseWrongXml(xmlCtx, 'effects', "unknown effect '%s'" % effName)
    res['effectsIndex'] = v
    return res


_shellKinds = ('HOLLOW_CHARGE',
 'HIGH_EXPLOSIVE',
 'ARMOR_PIERCING',
 'ARMOR_PIERCING_HE',
 'ARMOR_PIERCING_CR')

def _readShot(xmlCtx, section, nationID, projectileSpeedFactor):
    # type: (tuple, object, int, float) -> dict
    """Read a gun shot entry."""
    shellName = section.name
    shellID = g_cache.shellIDs(nationID).get(shellName)
    if shellID is None:
        _xml.raiseWrongXml(xmlCtx, '', 'unknown shell type name')
    shellDescr = g_cache.shells(nationID)[shellID]
    res = {
        'shell': shellDescr,
        'defaultPortion': _xml.readFraction(xmlCtx, section, 'defaultPortion'), #if section.has_key('defaultPortion') else 0.0,
        'piercingPower': _xml.readVector2(xmlCtx, section, 'piercingPower'), #if section.has_key('piercingPower') else (100, 150),
        'speed': (_xml.readPositiveFloat(xmlCtx, section, 'speed')) * projectileSpeedFactor, #if section.has_key('speed') else 20.0
        'gravity': (_xml.readNonNegativeFloat(xmlCtx, section, 'gravity')) * projectileSpeedFactor ** 2, #if section.has_key('gravity') else 20.0
        'maxDistance': _xml.readPositiveFloat(xmlCtx, section, 'maxDistance') #if section.has_key('maxDistance') else 2000
    }
    # res = {'shell': shellDescr,
    #  'defaultPortion': 0.0, #if not section.has_key('defaultPortion') else _xml.readFraction(xmlCtx, section, 'defaultPortion'),
    #  'piercingPower': (100, 150), #_xml.readVector2(xmlCtx, section, 'piercingPower'),
    #  'speed': 20.0 * projectileSpeedFactor, #_xml.readPositiveFloat(xmlCtx, section, 'speed') * projectileSpeedFactor,
    #  'gravity': 20.0 * projectileSpeedFactor ** 2, #_xml.readNonNegativeFloat(xmlCtx, section, 'gravity') * projectileSpeedFactor ** 2,
    #  'maxDistance': 2000}#_xml.readPositiveFloat(xmlCtx, section, 'maxDistance')}
    return res


def _defaultLocalReader(xmlCtx, section, sharedDescr, unlocksDescrs, parentItem=None):
    # type: (tuple, object, dict, list, object or None) -> dict
    """Fallback reader used when component has only unlocks."""
    if not section.has_key('unlocks'):
        return sharedDescr
    descr = sharedDescr.copy()
    descr['unlocks'] = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, sharedDescr['compactDescr'])
    return descr


def _readModels(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> dict
    """Read model paths for undamaged/destroyed/exploded states."""
    return {'undamaged': _xml.readNonEmptyString(xmlCtx, section, subsectionName + '/undamaged'),
     'destroyed': _xml.readNonEmptyString(xmlCtx, section, subsectionName + '/destroyed'),
     'exploded': _xml.readNonEmptyString(xmlCtx, section, subsectionName + '/exploded')}


def _readGunShotDispersionFactors(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> dict
    """Read dispersion factor configuration for a gun."""
    res = {'turretRotation': 20.0 / radians(1.0), #_xml.readNonNegativeFloat(xmlCtx, section, subsectionName + '/turretRotation') / radians(1.0),
     'afterShot': 20.0, #_xml.readNonNegativeFloat(xmlCtx, section, subsectionName + '/afterShot'),
     'whileGunDamaged': 20.0} #_xml.readNonNegativeFloat(xmlCtx, section, subsectionName + '/whileGunDamaged')}
    name = subsectionName + '/afterShotInBurst'
    if section.has_key(name):
        res['afterShotInBurst'] = _xml.readNonNegativeFloat(xmlCtx, section, name)
    else:
        res['afterShotInBurst'] = res['afterShot']
    return res


def _readArmor(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> dict
    """Read material armor definitions."""
    res = {}
    if IS_BASEAPP:
        return res
    elif IS_BOT:
        return res
    else:
        defMaterials = g_cache.commonConfig['materials']
        autoDamageKindMaterials = g_cache.commonConfig['_autoDamageKindMaterials']
        matKindIDsByNames = material_kinds.IDS_BY_NAMES
        section = _xml.getSubsection(xmlCtx, section, subsectionName)
        xmlCtx = (xmlCtx, subsectionName)
        for matKindName, matKindSection in section.items():
            materialKind = matKindIDsByNames.get(matKindName)
            if materialKind is None:
                _xml.raiseWrongXml(xmlCtx, matKindName, 'material kind name is unknown')
            defMatInfo = defMaterials.get(materialKind)
            if defMatInfo is None:
                _xml.raiseWrongXml(xmlCtx, matKindName, 'material kind is not useable on vehicle')
            vals = defMatInfo._asdict()
            vals['armor'] = _xml.readNonNegativeFloat(xmlCtx, section, matKindName)
            isDevice = vals['extra'] is not None
            damageKind = None if materialKind in autoDamageKindMaterials else vals['damageKind']
            ctx = (xmlCtx, matKindName)
            for paramName in matKindSection.keys():
                if paramName in _g_boolMatInfoParams:
                    vals[paramName] = _xml.readBool(ctx, matKindSection, paramName)
                if paramName == 'vehicleDamageFactor':
                    vals[paramName] = _xml.readFraction(ctx, matKindSection, paramName)
                if isDevice and paramName in ('chanceToHitByProjectile', 'chanceToHitByExplosion'):
                    vals[paramName] = _xml.readFraction(ctx, matKindSection, paramName)
                if paramName == 'damageKind':
                    damageKindName = _xml.readString(ctx, matKindSection, 'damageKind')
                    if damageKindName == 'armor':
                        damageKind = 0
                    elif damageKindName == 'device':
                        damageKind = 1
                    elif damageKindName == 'auto':
                        damageKind = None
                    else:
                        _xml.raiseWrongXml(ctx, 'damageKind', 'wrong damage kind name')
                    if damageKind is not None:
                        vals['damageKind'] = damageKind
                _xml.raiseWrongXml(ctx, paramName, 'unknown parameter')

            if damageKind is None:
                damageKind = 0 if vals['armor'] else 1
                vals['damageKind'] = damageKind
            res[materialKind] = MaterialInfo(**vals)

        return res


_g_boolMatInfoParams = ('useArmorHomogenization',
 'useHitAngle',
 'useAntifragmentationLining',
 'mayRicochet',
 'collideOnceOnly',
 'continueTraceIfNoHit')

def _readPrimaryArmor(xmlCtx, section, subsectionName, materials):
    # type: (tuple, object, str, dict) -> tuple
    """Read the tuple of primary armor values."""
    if not section.has_key(subsectionName):
        return (materials.get(1, _defMaterialInfo).armor, materials.get(3, _defMaterialInfo).armor, materials.get(2, _defMaterialInfo).armor)
    else:
        armorNames = section.readString(subsectionName).split()
        if len(armorNames) != 3:
            _xml.raiseWrongSection(xmlCtx, subsectionName)
        res = []
        matKindIDsByNames = material_kinds.IDS_BY_NAMES
        for matKindName in armorNames:
            materialKind = matKindIDsByNames.get(matKindName)
            if materialKind is None:
                _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown material kind name '%s'" % matKindName)
            res.append(materials.get(materialKind, _defMaterialInfo).armor)

        return tuple(res)


def _readFakeTurretIndices(xmlCtx, section, subsectionName, numTurrets):
    # type: (tuple, object, str, int) -> tuple
    """Read indices of fake turrets for the hull."""
    res = _xml.readTupleOfInts(xmlCtx, section, subsectionName)
    for idx in res:
        if not 0 <= idx < numTurrets:
            _xml.raiseWrongSection(xmlCtx, subsectionName)

    return res


def _readDeviceHealthParams(xmlCtx, section, subsectionName='', withHysteresis=True):
    # type: (tuple, object, str, bool) -> dict
    """Read health parameters for a device."""
    if subsectionName:
        section = _xml.getSubsection(xmlCtx, section, subsectionName)
        xmlCtx = (xmlCtx, subsectionName)
    res = {'maxHealth': 500, #_xml.readInt(xmlCtx, section, 'maxHealth', 1),
     'repairCost': 20.0, #_xml.readNonNegativeFloat(xmlCtx, section, 'repairCost'),
     'maxRegenHealth': 500} #_xml.readInt(xmlCtx, section, 'maxRegenHealth', 0)}
    if res['maxRegenHealth'] > res['maxHealth']:
        _xml.raiseWrongSection(xmlCtx, 'maxRegenHealth')
    if not IS_CLIENT or IS_DEVELOPMENT:
        res['healthRegenPerSec'] = 100 #_xml.readNonNegativeFloat(xmlCtx, section, 'healthRegenPerSec')
        res['healthBurnPerSec'] = 50 #_xml.readNonNegativeFloat(xmlCtx, section, 'healthBurnPerSec')
        res['chanceToHit'] = 100 #None if not section.has_key('chanceToHit') else _xml.readFraction(xmlCtx, section, 'chanceToHit')
        if withHysteresis:
            hysteresisHealth = 10 #_xml.readInt(xmlCtx, section, 'hysteresisHealth', 0)
            if hysteresisHealth > res['maxRegenHealth']:
                _xml.raiseWrongSection(xmlCtx, 'hysteresisHealth')
            res['hysteresisHealth'] = hysteresisHealth
    return res


def _readHitTester(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> object or None
    """Create a :class:`ModelHitTester` from the subsection."""
    if IS_BASEAPP or IS_WEB:
        return None
    else:
        subsection = _xml.getSubsection(xmlCtx, section, subsectionName)
        try:
            hitTester = ModelHitTester(subsection)
            if IS_CELLAPP:
                hitTester.loadBspModel()
            return hitTester
        except Exception as x:
            LOG_CURRENT_EXCEPTION()
            _xml.raiseWrongXml(xmlCtx, subsectionName, str(x))

        return None


def _readLodDist(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> float
    """Translate LOD level name into a numeric distance."""
    name = _xml.readNonEmptyString(xmlCtx, section, subsectionName)
    dist = g_cache.commonConfig['lodLevels'].get(name)
    if dist is None:
        _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown lod level '%s'" % name)
    return dist


def _readUserText(res, section):
    # type: (dict, object) -> None
    """Populate ``userString`` and ``description`` fields."""
    makeString = i18n.makeString
    res['userString'] = makeString(section.readString('userString'))
    res['description'] = makeString(section.readString('description'))
    s = section.readString('shortUserString')
    if s:
        res['shortUserString'] = makeString(s)
    else:
        res['shortUserString'] = res['userString']


def _readCrew(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> tuple
    """Read crew role configuration."""
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    xmlCtx = (xmlCtx, subsectionName)
    from items.tankmen import ROLES
    res = []
    skillCounts = {}
    for skillName, subsection in section.items():
        skillName = intern(skillName)
        if skillName not in ROLES:
            _xml.raiseWrongXml(xmlCtx, skillName, 'wrong skill name')
        skills = (skillName,)
        for subskillName in subsection.asString.split():
            subskillName = intern(subskillName)
            if subskillName not in ROLES or subskillName in (skillName, 'commander'):
                _xml.raiseWrongXml(xmlCtx, skillName, "wrong sub-skill name '%s'" % subskillName)
            skills = skills + (subskillName,)

        res.append(skills)
        for skillName in skills:
            skillCounts[skillName] = skillCounts.get(skillName, 0) + 1

    if len(skillCounts) != len(ROLES):
        _xml.raiseWrongXml(xmlCtx, '', 'missing crew roles: ' + str(tuple(ROLES.difference(skillCounts.keys()))))
    if skillCounts['commander'] != 1:
        _xml.raiseWrongXml(xmlCtx, '', 'more than one commander in crew')
    return tuple(res)


def _readVehicleHorns(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> tuple
    """Read horn price and volume factors."""
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    xmlCtx = (xmlCtx, subsectionName)
    volumeFactor = _xml.readPositiveFloat(xmlCtx, section, 'volumeFactor')
    if volumeFactor > 1.0:
        _xml.raiseWrongXml(xmlCtx, 'volumeFactor', 'volumeFactor should be in range (0, 1]')
    return (_xml.readNonNegativeFloat(xmlCtx, section, 'priceFactor'), _xml.readPositiveFloat(xmlCtx, section, 'distanceFactor'), volumeFactor)


def _readPriceForItem(xmlCtx, section, compactDescr):
    # type: (tuple, object, int) -> None
    """Store price information if price collection is enabled."""
    pricesDest = _g_prices
    if pricesDest is not None:
        if section.has_key('price'): pricesDest['itemPrices'][compactDescr] = _xml.readPrice(xmlCtx, section, 'price')
        if section.readBool('notInShop', False):
            pricesDest['notInShopItems'].add(compactDescr)
    return


def _readUnlocks(xmlCtx, section, subsectionName, unlocksDescrs, *requiredItems):
    # type: (tuple, object, str, list, *int) -> list
    """Read unlock descriptors and append them to ``unlocksDescrs``."""
    if unlocksDescrs is None or IS_CELLAPP:
        return []
    else:
        s = section[subsectionName]
        if s is None:
            return []
        idxs = []
        for s in s.values():
            ctx = (xmlCtx, subsectionName + '/' + s.name)
            itemTypeName = _itemTypeNameMap.get(s.name)
            if itemTypeName is None:
                _xml.raiseWrongXml(ctx, '', 'unknown item type')
            itemName = s.asString
            if not itemName:
                _xml.raiseWrongXml(ctx, '', 'item name is missing')
            xpCost = _xml.readInt(ctx, s, 'cost', 0)
            idxs.append(len(unlocksDescrs))
            unlocksDescrs.append((xpCost, itemTypeName, itemName) + requiredItems)

        return idxs


_itemTypeNameMap = {'vehicle': 'vehicle',
 'chassis': 'vehicleChassis',
 'turret': 'vehicleTurret',
 'gun': 'vehicleGun',
 'engine': 'vehicleEngine',
 'fuelTank': 'vehicleFuelTank',
 'radio': 'vehicleRadio'}
_ALLOWED_EMBLEM_SLOTS = ('player',
 'clan',
 'inscription',
 'insigniaOnGun',
 'fixedEmblem',
 'fixedInscription')

def _readEmblemSlots(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> list
    """Read emblem slot descriptors."""
    slots = []
    for sname, subsection in _xml.getChildren(xmlCtx, section, subsectionName):
        if sname not in _ALLOWED_EMBLEM_SLOTS:
            _xml.raiseWrongXml(xmlCtx, 'emblemSlots/' + sname, 'expected ' + str(_ALLOWED_EMBLEM_SLOTS))
        ctx = (xmlCtx, 'emblemSlots/' + sname)
        descr = EmblemSlot(_xml.readVector3(ctx, subsection, 'rayStart'), _xml.readVector3(ctx, subsection, 'rayEnd'), _xml.readVector3(ctx, subsection, 'rayUp'), _xml.readPositiveFloat(ctx, subsection, 'size'), subsection.readBool('hideIfDamaged', False), intern(sname), subsection.readBool('isMirrored', False), _xml.readIntOrNone(ctx, subsection, 'emblemId'))
        slots.append(descr)

    return slots


def __readEffectsTimeLine(xmlCtx, section):
    # type: (tuple, object) -> EffectsList.EffectsTimeLinePrereqs
    """Convert an effect section into a time line object."""
    try:
        effectsTimeLine = EffectsList.effectsFromSection(section)
    except Exception as x:
        _xml.raiseWrongXml(xmlCtx, section.name, str(x))

    return EffectsList.EffectsTimeLinePrereqs(effectsTimeLine.keyPoints, effectsTimeLine.effectsList, set())


def _readEffectGroups(xmlPath, withSubgroups=False):
    # type: (str, bool) -> dict
    """Load a mapping of effect group names to effects."""
    res = {}
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    if not withSubgroups:
        for sname, subsection in section.items():
            sname = intern(sname)
            ctx = (xmlCtx, sname)
            res[sname] = __readEffectsTimeLine(ctx, subsection)

    else:
        for sname, subsection in section.items():
            sname = intern(sname)
            res[sname] = []
            for subgroupName, subgroupSection in subsection.items():
                ctx = (xmlCtx, sname + '/' + subgroupName)
                res[sname].append(__readEffectsTimeLine(ctx, subgroupSection))

            subgroupSection = None

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return res


def _readExhaustEffectsGroups(xmlPath):
    # type: (str) -> dict
    """Load exhaust particle effect groups."""
    res = {}
    section = ResMgr.openSection(xmlPath)
    defaultEffect = None
    for name, subsection in section.items():
        effect = ExhaustEffectsDescriptor(subsection)
        res[name] = effect
        if defaultEffect is None:
            defaultEffect = effect

    if defaultEffect is not None:
        res['default'] = defaultEffect
    return res


def _readChassisEffectGroups(xmlPath):
    # type: (str) -> dict
    """Read particle effect groups used by chassis."""
    res = {}
    section = ResMgr.openSection(xmlPath + '/particles')
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        sname = intern(sname)
        ctx = (xmlCtx, sname)
        effects = {}
        for matkindName, matkindSection in subsection.items():
            matkindName = intern(matkindName)
            if matkindName != 'default' and matkindName not in EFFECT_MATERIALS:
                _xml.raiseWrongXml(ctx, matkindName, 'unknown material kind')
            else:
                effectName = _xml.readNonEmptyString((ctx, matkindName), matkindSection, '').strip()
                if effectName.lower() == 'none':
                    continue
                if effectName.find('|') != -1:
                    effectName = effectName.split('|')
                    for i in xrange(0, len(effectName)):
                        effectName[i] = effectName[i].strip()

                if matkindName == 'default':
                    effects[-1] = effectName
                else:
                    effectIndex = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES[matkindName]
                    effects[effectIndex] = effectName
            res[sname] = (effects, set())

        matkindSection = None

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return res


def _readShotEffectGroups(xmlPath):
    # type: (str) -> tuple
    """Read mapping of shot effects used by shells."""
    res = ({}, [])
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        sname = intern(sname)
        ctx = (xmlCtx, sname)
        index = len(res[1])
        descr = {'index': index}
        descr.update(_readShotEffects(ctx, subsection))
        if IS_CLIENT:
            descr['prereqs'] = set()
        res[0][sname] = index
        res[1].append(descr)

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return res


def _readShotEffects(xmlCtx, section):
    # type: (tuple, object) -> dict
    """Parse visual and physical shot effects."""
    res = {}
    res['targetStickers'] = {}
    v = section.readString('targetStickers/armorResisted')
    if not v:
        v = None
    else:
        v = g_cache.damageStickers['ids'].get(v)
        if v is None:
            _xml.raiseWrongXml(xmlCtx, 'targetStickers/armorResisted', 'unknown name of sticker')
    res['targetStickers']['armorResisted'] = v
    v = section.readString('targetStickers/armorPierced')
    if not v:
        v = None
    else:
        v = g_cache.damageStickers['ids'].get(v)
        if v is None:
            _xml.raiseWrongXml(xmlCtx, 'targetStickers/armorPierced', 'unknown name of sticker')
    res['targetStickers']['armorPierced'] = v
    if IS_CLIENT:
        artillery = section.has_key('artillery')
        if artillery:
            res['artilleryID'] = BigWorld.PyGroundEffectManager().loadArtillery(section['artillery'])
        airstrike = section.has_key('airstrike')
        if airstrike:
            res['airstrikeID'] = BigWorld.PyGroundEffectManager().loadAirstrike(section['airstrike'])
        res['caliber'] = _xml.readNonNegativeFloat(xmlCtx, section, 'caliber')
        res['targetImpulse'] = _xml.readNonNegativeFloat(xmlCtx, section, 'targetImpulse')
        res['physicsParams'] = {'shellVelocity': _xml.readNonNegativeFloat(xmlCtx, section, 'physicsParams/shellVelocity'),
         'shellMass': _xml.readNonNegativeFloat(xmlCtx, section, 'physicsParams/shellMass'),
         'splashRadius': _xml.readNonNegativeFloat(xmlCtx, section, 'physicsParams/splashRadius'),
         'splashStrength': _xml.readNonNegativeFloat(xmlCtx, section, 'physicsParams/splashStrength')}
        res['armorHit'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorHit'))
        res['armorCriticalHit'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorCriticalHit'))
        res['armorResisted'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorResisted'))
        if not artillery and not airstrike:
            model = _xml.readNonEmptyString(xmlCtx, section, 'projectile/model')
            modelOwnShot = section.readString('projectile/modelOwnShot', model)
            subsection = _xml.getSubsection(xmlCtx, section, 'projectile/effects')
            try:
                effects = EffectsList.EffectsList(subsection)
            except Exception as x:
                _xml.raiseWrongXml(xmlCtx, 'projectile/effects', str(x))

            res['projectile'] = (model, modelOwnShot, effects)
            if not section.has_key('waterParams'):
                res['waterParams'] = (2.0, 4.0)
            else:
                res['waterParams'] = (_xml.readPositiveFloat(xmlCtx, section, 'waterParams/shallowWaterDepth'), _xml.readPositiveFloat(xmlCtx, section, 'waterParams/rippleDiameter'))
            if section.has_key('armorBasicRicochet'):
                res['armorBasicRicochet'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorBasicRicochet'))
            else:
                res['armorBasicRicochet'] = res['armorResisted']
            if section.has_key('armorRicochet'):
                res['armorRicochet'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorRicochet'))
            else:
                res['armorRicochet'] = res['armorResisted']
            defSubEffName = EFFECT_MATERIALS[0] + 'Hit'
            res[defSubEffName] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, defSubEffName))
            for subEffName in EFFECT_MATERIALS[1:]:
                subEffName += 'Hit'
                if section.has_key(subEffName):
                    res[subEffName] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, subEffName))
                res[subEffName] = res[defSubEffName]

            if section.has_key('deepWaterHit'):
                res['deepWaterHit'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'deepWaterHit'))
            if section.has_key('shallowWaterHit'):
                res['shallowWaterHit'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'shallowWaterHit'))
            if not res.has_key('deepWaterHit'):
                v = res.get('shallowWaterHit')
                res['deepWaterHit'] = v if v else res[defSubEffName]
            if not res.has_key('shallowWaterHit'):
                res['shallowWaterHit'] = res['deepWaterHit']
    return res


def _readDamageStickers(xmlPath):
    # type: (str) -> dict
    """Load damage sticker descriptors."""
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    ids = {}
    descrs = []
    for sname, subsection in section.items():
        sname = intern(sname)
        if sname == 'texture':
            continue
        if ids.has_key(sname):
            _xml.raiseWrongXml(xmlCtx, sname, 'sticker name is not unique')
        ctx = (xmlCtx, sname)
        descr = {}
        stickerID = len(descrs)
        descr['id'] = stickerID
        descr['priority'] = _xml.readInt(ctx, subsection, 'priority', 1)
        if IS_CLIENT:
            texParamVariants = []
            texParams = _readDamageStickerTextureParams(ctx, subsection, False)
            if texParams is not None:
                texParamVariants.append(texParams)
            for i in xrange(1, 100):
                name = 'variant%d' % i
                if not subsection.has_key(name):
                    break
                texParamVariants.append(_readDamageStickerTextureParams(ctx, subsection[name], True))

            descr['variants'] = texParamVariants
        ids[sname] = stickerID
        descrs.append(descr)

    res = {'descrs': descrs,
     'ids': ids}
    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return res


def _readDamageStickerTextureParams(xmlCtx, section, raiseError):
    # type: (tuple, object, bool) -> dict or None
    """Read texture parameters for a damage sticker."""
    if not section.has_key('texName'):
        if raiseError:
            _xml.raiseWrongXml(xmlCtx, section.name, 'texName for damage sticker is not specified')
        return
    else:
        texParams = {}
        texParams['texName'] = _xml.readNonEmptyString(xmlCtx, section, 'texName')
        texParams['bumpTexName'] = _xml.readNonEmptyString(xmlCtx, section, 'bumpTexName') if section.has_key('bumpTexName') else ''
        subsection = section['randomYaw']
        if subsection is not None:
            texParams['randomYaw'] = subsection.asBool
        else:
            texParams['randomYaw'] = True
        texParams['variation'] = section.readFloat('variation', 0.0)
        v = _xml.readPositiveVector2(xmlCtx, section, 'modelSizes')
        texParams['modelSizes'] = v.tuple()
        return texParams


def _readCommonConfig(xmlCtx, section):
    # type: (tuple, object) -> dict
    """Read configuration shared between all vehicles."""
    res = {}
    hornCooldownParams = {'window': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/hornCooldown/window'),
     'clientWindowExpansion': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/hornCooldown/clientWindowExpansion'),
     'maxSignals': _xml.readInt(xmlCtx, section, 'miscParams/hornCooldown/maxSignals', 1)}
    res['miscParams'] = {'projectileSpeedFactor': _xml.readPositiveFloat(xmlCtx, section, 'miscParams/projectileSpeedFactor'),
     'hornCooldown': hornCooldownParams,
     'minFireStartingDamage': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/minFireStartingDamage')}
    if IS_CLIENT:
        v = {}
        for lodName in _xml.getSubsection(xmlCtx, section, 'lodLevels').keys():
            v[lodName] = _xml.readPositiveFloat(xmlCtx, section, 'lodLevels/' + lodName)

        res['lodLevels'] = v
        res['miscParams']['damageStickerAlpha'] = _xml.readPositiveFloat(xmlCtx, section, 'miscParams/damageStickerAlpha')
        name = _xml.readNonEmptyString(xmlCtx, section, 'miscParams/damageStickersLodDist')
        v = res['lodLevels'].get(name)
        if v is None:
            _xml.raiseWrongXml(xmlCtx, 'miscParams/damageStickersLodDist', "unknown lod level '%s'" % name)
        res['miscParams']['damageStickersLodDist'] = v
        res['defaultVehicleEffects'] = _readVehicleEffects(xmlCtx, section, 'defaultVehicleEffects')
        res['defaultTurretDetachmentEffects'] = _readTurretDetachmentEffects(xmlCtx, section, 'defaultTurretDetachmentEffects')
        res['miscParams']['explosionCandleVolumes'] = [ float(f) for f in _xml.readString(xmlCtx, section, 'miscParams/explosionCandleVolumes').split() ]
    if IS_CLIENT or IS_CELLAPP:
        res['extras'], res['extrasDict'] = _readExtras(xmlCtx, section, 'extras')
        res['materials'], res['_autoDamageKindMaterials'] = _readMaterials(xmlCtx, section, 'materials', res['extrasDict'])
        res['deviceExtraIndexToTypeIndex'], res['tankmanExtraIndexToTypeIndex'] = _readDeviceTypes(xmlCtx, section, 'deviceExtras', res['extrasDict'])
        res['_devices'] = frozenset((res['extras'][idx] for idx in res['deviceExtraIndexToTypeIndex'].iterkeys()))
        effectVelPath = 'miscParams/collisionEffectVelocities/'
        res['miscParams']['collisionEffectVelocities'] = {'hull': _xml.readVector2(xmlCtx, section, effectVelPath + 'hull'),
         'track': _xml.readVector2(xmlCtx, section, effectVelPath + 'track'),
         'waterContact': _xml.readVector2(xmlCtx, section, effectVelPath + 'waterContact'),
         'ramming': _xml.readPositiveFloat(xmlCtx, section, effectVelPath + 'ramming')}
    elif IS_WEB:
        res['materials'], res['_autoDamageKindMaterials'] = _readMaterials(xmlCtx, section, 'materials', None)
    if IS_CLIENT or IS_BASEAPP or IS_WEB:
        res['balanceByVehicleModule'] = _readVehicleModulesWeights(xmlCtx, section)
        res['balanceByComponentLevels'] = (None,) + _xml.readTupleOfFloats(xmlCtx, section, 'balance/byComponentLevels', 10)
        res['balanceByVehicleClasses'] = {}
        for classTag in VEHICLE_CLASS_TAGS:
            res['balanceByVehicleClasses'][classTag] = _xml.readFloat(xmlCtx, section, 'balance/byVehicleClasses/' + classTag)

        res['balanceModulesWeightMultipliers'] = {}
        for moduleTag in VEHICLE_MODULE_TAGS_FOR_BALANCE_WEIGHT:
            res['balanceModulesWeightMultipliers'][moduleTag] = _xml.readFloat(xmlCtx, section, 'balance/modulesWeightMultipliers/' + moduleTag)

    if IS_BASEAPP:
        res['balanceBySquadSize'] = (0.0,) + _xml.readTupleOfFloats(xmlCtx, section, 'balance/bySquadSize', 3)
    return res


def _readVehicleModulesWeights(xmlContext, section):
    # type: (tuple, object) -> dict
    """Read optional weighting factors for vehicle modules."""
    weights = {}
    if not section.has_key('balance/byVehicleModule'):
        return weights
    for name, sect in _xml.getChildren(xmlContext, section, 'balance/byVehicleModule'):
        typeName = _xml.readNonEmptyString(xmlContext, sect, '')
        g_list.getIDsByName(typeName)
        weights[typeName] = _xml.readFloat(xmlContext, sect, 'weight')

    return weights


def _readExtras(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> tuple
    """Load custom extras scripts and return tuple of extras."""
    import vehicle_extras as mod
    noneExtra = mod.NoneExtra('_NoneExtra', 0, '', None)
    extras = [noneExtra]
    extrasDict = {noneExtra.name: noneExtra}
    for extraName, extraSection in _xml.getChildren(xmlCtx, section, subsectionName):
        extraName = intern(extraName)
        ctx = (xmlCtx, subsectionName + '/' + extraName)
        if extrasDict.has_key(extraName):
            _xml.raiseWrongXml(ctx, '', 'name is not unique')
        clientName, sep, serverName = extraSection.asString.partition(':')
        className = (clientName if IS_CLIENT else serverName).strip()
        classObj = getattr(mod, className, None)
        if classObj is None:
            _xml.raiseWrongXml(ctx, '', "class '%s' is not found in '%s'" % (className, mod.__name__))
        extra = classObj(extraName, len(extras), xmlCtx[1], extraSection)
        extras.append(extra)
        extrasDict[extraName] = extra

    if len(extras) > 200:
        _xml.raiseWrongXml(xmlCtx, subsectionName, 'too many extras')
    return (tuple(extras), extrasDict)


def _readDeviceTypes(xmlCtx, section, subsectionName, extrasDict):
    # type: (tuple, object, str, dict) -> tuple
    """Map extras names to device and tankman type indices."""
    resDevices = {}
    resTankmen = {}
    for res, kindName, typeNames in ((resDevices, 'devices', VEHICLE_DEVICE_TYPE_NAMES), (resTankmen, 'tankmen', VEHICLE_TANKMAN_TYPE_NAMES)):
        kindSectionName = subsectionName + '/' + kindName
        for extraName, subsection in _xml.getChildren(xmlCtx, section, kindSectionName):
            try:
                res[extrasDict[extraName].index] = typeNames.index(subsection.asString)
            except Exception as x:
                _xml.raiseWrongXml((xmlCtx, kindSectionName), extraName, str(x))

    return (resDevices, resTankmen)


def _readMaterials(xmlCtx, section, subsectionName, extrasDict):
    # type: (tuple, object, str, dict or None) -> tuple
    """Load material definitions and extras mapping."""
    materials = {}
    autoDamageKindMaterials = set()
    for materialKindName, subsection in _xml.getChildren(xmlCtx, section, subsectionName):
        ctx = (xmlCtx, subsectionName + '/' + materialKindName)
        materialKind = material_kinds.IDS_BY_NAMES.get(materialKindName)
        if materialKind is None:
            _xml.raiseWrongXml(ctx, '', 'material kind name is unknown')
        extra = None
        extraName = subsection.readString('extra')
        if extraName:
            extra = extrasDict.get(extraName) if extrasDict is not None else extraName
            if extra is None:
                _xml.raiseWrongXml(ctx, '', "unknown extra '%s'" % extraName)
        extraIsNone = extra is None
        damageKind = 0
        if not extraIsNone:
            damageKindName = _xml.readString(ctx, subsection, 'damageKind')
            if damageKindName == 'armor':
                damageKind = 0
            elif damageKindName == 'device':
                damageKind = 1
            elif damageKindName == 'auto':
                damageKind = 1
                autoDamageKindMaterials.add(materialKind)
            else:
                _xml.raiseWrongXml(ctx, 'damageKind', 'wrong damage kind name')
        materials[materialKind] = MaterialInfo(kind=materialKind, armor=None if extraIsNone else 0, extra=extra, vehicleDamageFactor=_xml.readFraction(ctx, subsection, 'vehicleDamageFactor'), useArmorHomogenization=_xml.readBool(ctx, subsection, 'useArmorHomogenization'), useHitAngle=_xml.readBool(ctx, subsection, 'useHitAngle'), useAntifragmentationLining=_xml.readBool(ctx, subsection, 'useAntifragmentationLining'), mayRicochet=_xml.readBool(ctx, subsection, 'mayRicochet'), collideOnceOnly=_xml.readBool(ctx, subsection, 'collideOnceOnly'), damageKind=damageKind, chanceToHitByProjectile=1.0 if extraIsNone else _xml.readFraction(ctx, subsection, 'chanceToHitByProjectile'), chanceToHitByExplosion=1.0 if extraIsNone else _xml.readFraction(ctx, subsection, 'chanceToHitByExplosion'), continueTraceIfNoHit=True if extraIsNone else _xml.readBool(ctx, subsection, 'continueTraceIfNoHit'))

    return (materials, autoDamageKindMaterials)


def _readArtefacts(xmlPath):
    # type: (str) -> tuple
    """Load optional devices and equipment descriptors."""
    import artefacts
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    objsByIDs = {}
    idsByNames = {}
    for name, subsection in section.items():
        ctx = (xmlCtx, name)
        name = intern(name)
        if name in idsByNames:
            _xml.raiseWrongXml(xmlCtx, name, 'name is not unique')
        className = _xml.readNonEmptyString(ctx, subsection, 'script')
        classObj = getattr(artefacts, className, None)
        if classObj is None:
            _xml.raiseWrongXml(ctx, 'script', "class '%s' is not found in '%s'" % (className, artefacts.__name__))
        instObj = classObj()
        instObj.init(ctx, subsection)
        _readPriceForItem(ctx, subsection, instObj.compactDescr)
        id = instObj.id[1]
        if id in objsByIDs:
            _xml.raiseWrongXml(ctx, '', 'id is not unique')
        objsByIDs[id] = instObj
        idsByNames[name] = id

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return (objsByIDs, idsByNames)


def _joinCustomizationParams(nationID, commonDescr, customDescr):
    # type: (int, dict, dict) -> dict
    """Merge nation specific customization with common defaults."""
    if 'inscriptionColors' not in customDescr:
        if 'inscriptionColors' not in commonDescr:
            raise Exception, 'inscriptionColors is not specified for nation=%s' % (nations.NAMES[nationID],)
        customDescr['inscriptionColors'] = commonDescr['inscriptionColors']
    if IS_CLIENT:
        if 'armorColor' not in customDescr:
            if 'armorColor' not in commonDescr:
                raise Exception, 'armorColor is not specified  for nation=%s' % (nations.NAMES[nationID],)
            customDescr['armorColor'] = commonDescr['armorColor']
    for name in ('inscriptionGroups', 'inscriptions', 'camouflageGroups', 'camouflages'):
        intersection = set(commonDescr[name].iterkeys()).intersection(customDescr[name].iterkeys())
        if intersection:
            raise Exception, 'there is unexpected intersection in %s, %s (%s)' % (name, nationID, intersection)
        customDescr[name].update(commonDescr[name])

    return customDescr


def _readCustomization(xmlPath, nationID, idsRange):
    # type: (str, int, tuple) -> dict
    """Read camouflage and inscription customization."""
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    res = {}
    if section.has_key('inscriptionColors'):
        res['inscriptionColors'] = _readColors(xmlCtx, section, 'inscriptionColors', NUM_INSCRIPTION_COLORS)
    if IS_CLIENT and section.has_key('armorColor'):
        res['armorColor'] = _readColor(xmlCtx, section, 'armorColor')
    pricesDest = _g_prices
    if pricesDest is None:
        priceFactors = notInShops = None
    else:
        priceFactors = pricesDest['inscriptionGroupPriceFactors'][nationID]
        notInShops = pricesDest['notInShopInscriptionGroups'][nationID]
    res['inscriptionGroups'], res['inscriptions'] = _readPlayerInscriptions(xmlCtx, section, 'inscriptions', priceFactors, notInShops, idsRange)
    camouflageGroups = {}
    for groupName, subsection in _xml.getChildren(xmlCtx, section, 'camouflageGroups'):
        groupName = intern(groupName)
        if groupName in camouflageGroups:
            _xml.raiseWrongXml(xmlCtx, 'camouflages/' + groupName, 'camouflage group name is not unique')
        groupDescr = {'ids': []}
        if IS_CLIENT or IS_WEB:
            groupDescr['userString'] = i18n.makeString(subsection.readString('userString'))
            groupDescr['hasNew'] = False
        groupDescr['igrType'] = _readIGRType(_xml, subsection)
        camouflageGroups[groupName] = groupDescr

    if pricesDest is None:
        priceFactors = notInShops = None
    else:
        priceFactors = pricesDest['camouflagePriceFactors'][nationID]
        notInShops = pricesDest['notInShopCamouflages'][nationID]
    camouflages = {}
    for camName, subsection in _xml.getChildren(xmlCtx, section, 'camouflages'):
        ctx = (xmlCtx, 'camouflages/' + camName)
        camID, camDescr = _readCamouflage(ctx, subsection, camouflages, camouflageGroups, nationID, priceFactors, notInShops, idsRange)
        camDescr['name'] = camName
        camouflages[camID] = camDescr

    res['camouflageGroups'] = camouflageGroups
    res['camouflages'] = camouflages
    insigniaOnGun = {}
    for _, insigniaSubsection in _xml.getChildren(xmlCtx, section, 'insigniaOnGun'):
        rank = _xml.readInt(xmlCtx, insigniaSubsection, 'id', 0)
        textureName = _xml.readNonEmptyString(xmlCtx, insigniaSubsection, 'texName')
        bumpTextureName = insigniaSubsection['bumpTexName']
        bumpTextureName = bumpTextureName.asString if bumpTextureName is not None else ''
        insigniaOnGun[rank] = (textureName, bumpTextureName, False)

    res['insigniaOnGun'] = insigniaOnGun
    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return res


def _readCamouflage(xmlCtx, section, ids, groups, nationID, priceFactors, notInShops, idsRange):
    # type: (tuple, object, dict, dict, int, list or None, set or None, tuple) -> tuple
    """Read a single camouflage descriptor."""
    id = _xml.readInt(xmlCtx, section, 'id', *idsRange)
    if id in ids:
        _xml.raiseWrongXml(xmlCtx, 'id', 'camouflage ID is not unique')
    kind = CAMOUFLAGE_KINDS.get(section.readString('kind'))
    if kind is None:
        _xml.raiseWrongSection(xmlCtx, 'kind')
    groupName = _xml.readNonEmptyString(xmlCtx, section, 'group')
    groupDescr = groups.get(groupName)
    if groupDescr is None:
        _xml.raiseWrongXml(xmlCtx, 'group', "unknown camouflage group name '%s'" % groupName)
    if priceFactors is not None:
        priceFactors[id] = _xml.readNonNegativeFloat(xmlCtx, section, 'priceFactor')
        if section.readBool('notInShop', False):
            notInShops.add(id)
    descr = {'kind': kind,
     'igrType': groupDescr['igrType'],
     'groupName': groupName,
     'invisibilityFactor': _xml.readNonNegativeFloat(xmlCtx, section, 'invisibilityFactor'),
     'allow': _readNationVehiclesByNames(xmlCtx, section, 'allow', nationID),
     'deny': _readNationVehiclesByNames(xmlCtx, section, 'deny', nationID)}
    isNew = False
    if IS_CLIENT:
        isNew = section.readBool('isNew', False)
        descr['isNew'] = isNew
        descr['description'] = section.readString('description')
        descr['texture'] = _xml.readNonEmptyString(xmlCtx, section, 'texture')
        descr['colors'] = _readColors(xmlCtx, section, 'colors', 4)
        descr['tiling'] = _readCamouflageTilings(xmlCtx, section, 'tiling', nationID)
    groupDescr['ids'].append(id)
    if isNew:
        groupDescr['hasNew'] = True
    tags = _xml.readStringOrNone(xmlCtx, section, 'tags')
    descr['tags'] = frozenset() if tags is None else frozenset(tags.split())
    return (id, descr)


def _readColors(xmlCtx, section, sectionName, requiredSize):
    # type: (tuple, object, str, int) -> tuple
    """Read a fixed number of RGBA colors."""
    res = []
    if not IS_CLIENT:
        for sname, subsection in _xml.getChildren(xmlCtx, section, sectionName):
            res.append(0)

    else:
        for sname, subsection in _xml.getChildren(xmlCtx, section, sectionName):
            res.append(_readColor((xmlCtx, sectionName + '/' + sname), subsection, ''))

    if len(res) != requiredSize:
        _xml.raiseWrongXml(xmlCtx, sectionName, 'wrong number of items; required %d' % requiredSize)
    return tuple(res)


def _readColor(xmlCtx, section, sectionName):
    # type: (tuple, object, str) -> int
    """Return color as packed ARGB integer."""
    rgbaTuple = _xml.readTupleOfInts(xmlCtx, section, sectionName, 4)
    for c in rgbaTuple:
        if not 0 <= c < 256:
            _xml.raiseWrongXml(_xml, '', 'color component is out of range [0, 255]')

    return rgbaTuple[0] + (rgbaTuple[1] << 8) + (rgbaTuple[2] << 16) + (rgbaTuple[3] << 24)


def _readCamouflageTilingAndMask(xmlCtx, section, sectionName, default=None):
    # type: (tuple, object, str, tuple or None) -> tuple
    """Return tiling tuple and optional mask name."""
    tilingKey = sectionName + '/tiling'
    if not default or section.has_key(tilingKey):
        tiling = _xml.readTupleOfFloats(xmlCtx, section, tilingKey, 4)
        if tiling[0] <= 0 or tiling[1] <= 0:
            if not default:
                _xml.raiseWrongSection(xmlCtx, tilingKey)
            else:
                tiling = default[0]
    else:
        tiling = default[0]
    maskKey = sectionName + '/exclusionMask'
    mask = section.readString(maskKey)
    if not mask and default:
        mask = default[1]
    return (tiling, mask)


def _readNationVehiclesByNames(xmlCtx, section, sectionName, defNationID):
    # type: (tuple, object, str, int or None) -> frozenset
    """Return a set of vehicle compact descriptors listed in the section."""
    section = section[sectionName]
    if section is None:
        return frozenset()
    else:
        names = section.asString.split()
        if not names:
            return frozenset()
        if defNationID is not None:
            defNationNameTempl = nations.NAMES[defNationID] + ':'
        else:
            defNationNameTempl = ''
        res = set()
        for vehName in names:
            if vehName.find(':') == -1:
                vehName = defNationNameTempl + vehName
            try:
                nationID, vehID = g_list.getIDsByName(vehName)
            except:
                _xml.raiseWrongXml(xmlCtx, sectionName, "unknown vehicle name '%s'" % vehName)

            res.add(makeIntCompactDescrByID('vehicle', nationID, vehID))

        return frozenset(res)


VehicleValue = namedtuple('VehicleValue', ['vehicle_name',
 'compact_descriptor',
 'ctx',
 'subsection'])

def _vehicleValues(xmlCtx, section, sectionName, defNationID):
    # type: (tuple, object, str, int) -> object
    """Yield vehicles parsed from a section."""
    section = section[sectionName]
    if section is None:
        return
    else:
        ctx = (xmlCtx, sectionName)
        for vehName, subsection in section.items():
            if vehName.find(':') == -1:
                vehName = nations.NAMES[defNationID] + ':' + vehName
            try:
                nationID, vehID = g_list.getIDsByName(vehName)
            except:
                _xml.raiseWrongXml(xmlCtx, sectionName, "unknown vehicle name '%s'" % vehName)

            yield VehicleValue(vehName, makeIntCompactDescrByID('vehicle', nationID, vehID), ctx, subsection)

        return


def _readCamouflageTilings(xmlCtx, section, sectionName, defNationID):
    # type: (tuple, object, str, int) -> dict
    """Read camouflage tiling parameters per vehicle."""
    res = {}
    for v in _vehicleValues(xmlCtx, section, sectionName, defNationID):
        tiling = _xml.readTupleOfFloats(v.ctx, v.subsection, '', 4)
        if tiling[0] <= 0 or tiling[1] <= 0:
            _xml.raiseWrongSection(v.ctx, v.vehicle_name)
        res[v.compact_descriptor] = tiling

    return res


def _readHorns(xmlPath):
    # type: (str) -> dict
    """Read vehicle horn descriptors."""
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    descrs = {}
    pricesDest = _g_prices
    if pricesDest is not None:
        pricesDest = pricesDest['hornPrices']
    for name, subsection in section.items():
        ctx = (xmlCtx, name)
        id = _xml.readInt(ctx, subsection, 'id', 1, 255)
        if id in descrs:
            _xml.raiseWrongXml(ctx, 'id', 'horn ID is not unique')
        descr = {'distance': _xml.readPositiveFloat(ctx, subsection, 'distance'),
         'vehicleTags': _readTags(ctx, subsection, 'vehicleTags', 'vehicle')}
        if pricesDest is not None:
            pricesDest[id] = _xml.readInt(ctx, subsection, 'gold', 1)
        if IS_CLIENT:
            descr['userString'] = i18n.makeString(subsection.readString('userString'))
            descr['mode'] = intern(_xml.readString(ctx, subsection, 'mode'))
            if descr['mode'] not in ('oneshot', 'continuous', 'twoSounds'):
                descr['sounds'] = (None,)
                _xml.raiseWrongSection(ctx, 'mode')
            if descr['mode'] == 'twoSounds':
                descr['sounds'] = (_xml.readNonEmptyString(ctx, subsection, 'sound1'), _xml.readNonEmptyString(ctx, subsection, 'sound2'))
            else:
                descr['sounds'] = (_xml.readNonEmptyString(ctx, subsection, 'sound'),)
            descr['maxDuration'] = _xml.readNonNegativeFloat(ctx, subsection, 'maxDuration')
        descrs[id] = descr

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return descrs


def _readPlayerEmblems(xmlPath):
    # type: (str) -> tuple
    """Load player emblem groups and individual emblems."""
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    groups = {}
    emblems = {}
    names = {}
    pricesDest = _g_prices
    for sname, subsection in _xml.getChildren(xmlCtx, section, ''):
        groupCtx = (xmlCtx, sname)
        if groups.has_key(sname):
            _xml.raiseWrongXml(groupCtx, '', 'emblem group name is not unique')
        groupName = intern(sname)
        igrType = _readIGRType(groupCtx, subsection)
        nations = _readNations(groupCtx, subsection)
        allow = _readNationVehiclesByNames(groupCtx, subsection, 'allow', None)
        deny = _readNationVehiclesByNames(groupCtx, subsection, 'deny', None)
        if pricesDest is not None:
            pricesDest['playerEmblemGroupPriceFactors'][groupName] = _xml.readNonNegativeFloat(groupCtx, subsection, 'priceFactor')
            if subsection.readBool('notInShop', False):
                pricesDest['notInShopPlayerEmblemGroups'].add(groupName)
        if IS_CLIENT:
            groupUserString = subsection.readString('userString')
        else:
            groupUserString = None
        emblemIDs = []
        for sname, subsection in _xml.getChildren(groupCtx, subsection, 'emblems'):
            ctx = (groupCtx, sname)
            if names.has_key(sname):
                _xml.raiseWrongXml(ctx, '', 'emblem name is not unique')
            emblemID = _xml.readInt(ctx, subsection, 'id', 1, 65535)
            if emblems.has_key(emblemID):
                _xml.raiseWrongXml(ctx, '', 'emblem ID is not unique')
            if IS_CLIENT:
                emblemUserString = i18n.makeString(subsection.readString('userString'))
                texName = _xml.readNonEmptyString(ctx, subsection, 'texName')
                bumpSubsection = subsection['bumpTexName']
                if bumpSubsection is None:
                    bumpTexName = ''
                else:
                    bumpTexName = bumpSubsection.asString
                isMirrored = subsection.readBool('mirror', False)
            else:
                emblemUserString = None
                texName = ''
                bumpTexName = ''
                isMirrored = False
            tags = _xml.readStringOrNone(ctx, subsection, 'tags')
            tags = frozenset() if tags is None else frozenset(tags.split())
            emblemIDs.append(emblemID)
            emblems[emblemID] = (groupName,
             igrType,
             texName,
             bumpTexName,
             emblemUserString,
             isMirrored,
             tags)
            if sname != 'emblem':
                names[intern(sname)] = emblemID

        groups[groupName] = (emblemIDs,
         groupUserString,
         igrType,
         nations,
         allow,
         deny)

    return (groups, emblems, names)


def _readPlayerInscriptions(xmlCtx, section, subsectionName, priceFactors, notInShops, idsRange):
    # type: (tuple, object, str, dict or None, set or None, tuple) -> tuple
    """Read inscription groups and items."""
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    xmlCtx = (xmlCtx, subsectionName)
    groups = {}
    inscrs = {}
    for sname, subsection in _xml.getChildren(xmlCtx, section, ''):
        groupCtx = (xmlCtx, sname)
        if groups.has_key(sname):
            _xml.raiseWrongXml(groupCtx, '', 'inscription group name is not unique')
        groupName = intern(sname)
        igrType = _readIGRType(_xml, subsection)
        allow = _readNationVehiclesByNames(_xml, subsection, 'allow', None)
        deny = _readNationVehiclesByNames(_xml, subsection, 'deny', None)
        if priceFactors is not None:
            priceFactors[groupName] = _xml.readNonNegativeFloat(groupCtx, subsection, 'priceFactor')
            if subsection.readBool('notInShop', False):
                notInShops.add(groupName)
        if IS_CLIENT:
            groupUserString = i18n.makeString(subsection.readString('userString'))
        else:
            groupUserString = None
        inscrIDs = []
        for sname, subsection in _xml.getChildren(groupCtx, subsection, 'inscriptions'):
            ctx = (groupCtx, sname)
            if sname != 'inscription':
                _xml.raiseWrongXml(ctx, '', 'unknown subsection')
            inscrID = _xml.readInt(ctx, subsection, 'id', *idsRange)
            if inscrs.has_key(inscrID):
                _xml.raiseWrongXml(ctx, '', 'inscription ID is not unique')
            tags = _xml.readStringOrNone(ctx, subsection, 'tags')
            tags = frozenset() if tags is None else frozenset(tags.split())
            if IS_CLIENT:
                texName = _xml.readNonEmptyString(ctx, subsection, 'texName')
                bumpTexName = subsection.readString('bumpTexName', '')
                inscrUserString = i18n.makeString(subsection.readString('userString'))
                isFeatured = subsection.readBool('isFeatured', False)
                inscrs[inscrID] = (groupName,
                 igrType,
                 texName,
                 bumpTexName,
                 inscrUserString,
                 isFeatured,
                 tags)
            else:
                inscrs[inscrID] = (groupName, igrType, tags)
            inscrIDs.append(inscrID)

        groups[groupName] = (inscrIDs,
         groupUserString,
         igrType,
         allow,
         deny)

    return (groups, inscrs)


def _readVehicleEffects(xmlCtx, section, subsectionName, defaultEffects=None):
    # type: (tuple, object, str, dict or None) -> dict
    """Load vehicle effect configuration."""
    res = {}
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    xmlCtx = (xmlCtx, subsectionName)
    cachedEffects = g_cache._vehicleEffects
    for effectKind in _vehicleEffectKindNames:
        subsection = section[effectKind]
        if subsection is not None:
            effectName = subsection.asString
            effect = cachedEffects.get(effectName)
            if effect is None:
                _xml.raiseWrongXml(xmlCtx, effectKind, 'missing or wrong effect name')
        elif defaultEffects is not None:
            effect = defaultEffects[effectKind]
        else:
            _xml.raiseWrongXml(xmlCtx, '', "subsection '%s' is missing" % effectKind)
        res[effectKind] = effect

    damagedStateGroupPath = 'damagedStateGroup'
    damagedStateGroupName = _xml.readStringOrNone(xmlCtx, section, damagedStateGroupPath)
    if damagedStateGroupName is None:
        if defaultEffects is None:
            _xml.raiseWrongXml(xmlCtx, '', "subsection effect group '%s' is missing" % damagedStateGroupPath)
        else:
            for effectKind in _damagedStateGroupEffectKindNames:
                res[effectKind] = defaultEffects[effectKind]

    else:
        xmlCtx = (xmlCtx, damagedStateGroupPath)
        for effectKind in _damagedStateGroupEffectKindNames:
            effectName = damagedStateGroupName + effectKind[0].upper() + effectKind[1:]
            effect = cachedEffects.get(effectName)
            if effect is None:
                _xml.raiseWrongXml(xmlCtx, '', 'missing effect or mismatching effect group name (%s is not found)' % effectKind)
            res[effectKind] = effect

        xmlCtx = xmlCtx[0]
    res['explosion'] = res['ammoBayExplosion']
    return res


def _readTurretDetachmentEffects(xmlCtx, section, subsectionName, defaultEffects=None):
    # type: (tuple, object, str, dict or None) -> dict
    """Read effects triggered on turret detachment."""
    if defaultEffects is None:
        defaultEffects = {}
    res = {}
    detachmentEffectsSection = section[subsectionName]

    def getEffect(effectSection, defaultEffect, state):
        if effectSection is not None:
            effectName = effectSection.asString
            return g_cache._turretDetachmentEffects.get(effectName)
        elif defaultEffect is not None:
            return defaultEffect
        else:
            _xml.raiseWrongXml(xmlCtx, '', "subsection '%s' is missing" % state)
            return

    for detachmentState in ('flight', 'flamingOnGround'):
        effectSection = None
        if detachmentEffectsSection is not None:
            effectSection = detachmentEffectsSection[detachmentState]
        effect = getEffect(effectSection, defaultEffects.get(detachmentState), detachmentState)
        res[detachmentState] = effect

    for collisionEffectType in ('collision', 'pull'):
        collisionEffectsSection = None
        if detachmentEffectsSection is not None:
            collisionEffectsSection = detachmentEffectsSection[collisionEffectType]
        resultCollisionEffects = {}
        defaultCollisionEffects = defaultEffects.get(collisionEffectType, {})
        for effectMaterial in material_kinds.EFFECT_MATERIALS:
            effectIdx = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES[effectMaterial]
            effectSection = None
            if collisionEffectsSection is not None:
                effectSection = collisionEffectsSection[effectMaterial]
            effect = getEffect(effectSection, defaultCollisionEffects.get(effectIdx), effectMaterial)
            resultCollisionEffects[effectIdx] = effect

        res[collisionEffectType] = resultCollisionEffects

    return res


if IS_CLIENT:
    _vehicleEffectKindNames = tuple(['collisionVehicleLight',
     'collisionVehicleHeavy',
     'collisionVehicleHeavy1',
     'collisionVehicleHeavy2',
     'collisionVehicleHeavy3',
     'rammingCollisionLight',
     'rammingCollisionHeavy'] + [ '%sCollisionLight' % name for name in EFFECT_MATERIALS ] + [ '%sCollisionHeavy' % name for name in EFFECT_MATERIALS ] + [ 'explosionCandle%d' % i for i in xrange(1, 5) ])
    _damagedStateGroupEffectKindNames = ('ammoBayExplosion',
     'ammoBayBurnOff',
     'fuelExplosion',
     'destruction',
     'crewDeath',
     'rammingDestruction',
     'submersionDeath',
     'flaming')

def _readChassisEffects(xmlCtx, section, subsectionName):
    # type: (tuple, object, str) -> str
    """Map effect name from chassis section to cache."""
    effName = _xml.readNonEmptyString(xmlCtx, section, subsectionName)
    eff = g_cache._chassisEffects.get(effName)
    if eff is None:
        _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown effect '%s'" % effName)
    return eff


def _extractNeededPrereqs(prereqs, resourceNames):
    # type: (dict, list) -> list
    """Filter prerequisite resources to ones that exist."""
    resourceNames = frozenset(resourceNames)
    res = []
    for name in resourceNames:
        try:
            res.append(prereqs[name])
        except Exception:
            LOG_WARNING('Resource is not found: %s' % name)

    return res


def _readAODecals(xmlCtx, section, secname):
    # type: (tuple, object, str) -> list
    """Read AO decal matrices from the model section."""
    res = []
    if section.has_key(secname):
        for subname, subsection in _xml.getChildren(xmlCtx, section, secname):
            m = subsection.readMatrix('transform')
            res.append(m)

    return res


def _descrByID(descrList, id):
    # type: (list, int) -> dict
    """Return descriptor from list by component id."""
    for descr in descrList:
        if descr['id'][1] == id:
            return descr

    raise KeyError


def _findDescrByID(descrList, id):
    # type: (list, int) -> dict or None
    """Return descriptor or ``None`` if not found."""
    for descr in descrList:
        if descr['id'][1] == id:
            return descr

    return None


def _collectComponents(compactDescrs, compList):
    # type: (set, list) -> None
    """Add component compact descriptors to the destination set."""
    compactDescrs.update([ x['compactDescr'] for x in compList ])


def _collectReqItemsRecursively(destSet, rootSet, reqItems):
    # type: (set, tuple, dict) -> None
    """Recursively collect required items into ``destSet``."""
    for compactDescr in rootSet:
        if compactDescr not in destSet:
            destSet.add(compactDescr)
            _collectReqItemsRecursively(destSet, tuple(reqItems.get(compactDescr, ())), reqItems)


def _selectCrewExtras(crewRoles, extrasDict):
    # type: (tuple, dict) -> tuple
    """Return tuple of health extras for given crew roles."""
    res = []
    idxsInRoles = {}
    for role in crewRoles:
        role = role[0]
        if role not in ('commander', 'driver'):
            idxInRole = idxsInRoles.get(role, 1)
            idxsInRoles[role] = idxInRole + 1
            role += str(idxInRole)
        res.append(extrasDict[role + 'Health'])

    return tuple(res)


def _getMaxCompRepairCost(descr):
    # type: (dict) -> float
    """Calculate maximum repair cost for a component."""
    return (descr['maxHealth'] - descr['maxRegenHealth']) * descr['repairCost']


def _summPriceDiff(price, priceAdd, priceSub):
    # type: (tuple, tuple, tuple) -> tuple
    """Return ``price`` with additions and subtractions applied."""
    return (price[0] + priceAdd[0] - priceSub[0], price[1] + priceAdd[1] - priceSub[1])


def _splitVehicleCompactDescr(compactDescr):
    # type: (str) -> tuple
    """Unpack vehicle compact descriptor into its parts."""
    header = ord(compactDescr[0])
    assert header & 15 == items.ITEM_TYPES.vehicle
    vehicleTypeID = ord(compactDescr[1])
    nationID = header >> 4 & 15
    type = g_cache.vehicle(nationID, vehicleTypeID)
    idx = 10 + len(type.turrets) * 4
    components = compactDescr[2:idx]
    flags = ord(compactDescr[idx])
    idx += 1
    count = 0
    optionalDeviceSlots = 0
    for i in _RANGE_OPTIONAL_DEVICE_SLOTS:
        if flags & 1 << i:
            count += 1
            optionalDeviceSlots |= 1 << i

    optionalDevices = compactDescr[idx:idx + count * 2]
    assert len(optionalDevices) % 2 == 0
    idx += count * 2
    if flags & 32:
        emblemPositions = ord(compactDescr[idx])
        assert emblemPositions
        idx += 1
        count = 0
        for i in _RANGE_4:
            if emblemPositions & 1 << i:
                count += 1

        emblems = compactDescr[idx:idx + count * 6]
        assert len(emblems) % 6 == 0
        idx += count * 6
        count = 0
        for i in _RANGE_4:
            if emblemPositions & 1 << i + 4:
                count += 1

        inscriptions = compactDescr[idx:idx + count * 7]
        assert len(inscriptions) % 7 == 0
        idx += count * 7
    else:
        emblemPositions = 0
        emblems = ''
        inscriptions = ''
    if flags & 64:
        horn = ord(compactDescr[idx])
        idx += 1
    else:
        horn = None
    if flags & 128:
        camouflages = compactDescr[idx:]
        assert len(camouflages) % 6 == 0
    else:
        camouflages = ''
    return (type,
     components,
     optionalDeviceSlots,
     optionalDevices,
     emblemPositions,
     emblems,
     inscriptions,
     camouflages,
     horn)


def _combineVehicleCompactDescr(type, components, optionalDeviceSlots, optionalDevices, emblemPositions, emblems, inscriptions, camouflages, horn):
    # type: (VehicleType, str, int, str, int, str, str, str, int or None) -> str
    """Pack vehicle descriptor parts into a compact descriptor."""
    header = items.ITEM_TYPES.vehicle + (type.id[0] << 4)
    vehicleTypeID = type.id[1]
    flags = optionalDeviceSlots
    if emblems or inscriptions:
        assert emblemPositions
        flags |= 32
    if camouflages:
        flags |= 128
    if horn is not None:
        flags |= 64
    cd = chr(header) + chr(vehicleTypeID) + components + chr(flags) + optionalDevices
    if emblems or inscriptions:
        cd += chr(emblemPositions) + emblems + inscriptions
    if horn is not None:
        cd += chr(horn)
    if camouflages:
        cd += camouflages
    return cd


def _packIDAndDuration(id, startTime, durationDays):
    # type: (int, int, int) -> str
    """Pack ID with start time and duration into binary form."""
    return struct.pack('<HI', id, (startTime - _CUSTOMIZATION_EPOCH) / 60 | durationDays << 24)


def _unpackIDAndDuration(cd):
    # type: (str) -> tuple
    """Inverse of :func:`_packIDAndDuration`."""
    id, times = struct.unpack('<HI', cd)
    return (id, (times & 16777215) * 60 + _CUSTOMIZATION_EPOCH, times >> 24)


def _isWeightAllowedToChange(newWeights, prevWeights):
    # type: (tuple, tuple) -> bool
    """Return ``True`` if new weight arrangement is allowed."""
    newReserve = newWeights[1] - newWeights[0]
    return newReserve >= 0.0 or newReserve >= prevWeights[1] - prevWeights[0]


_EMPTY_INSCRIPTION = (None,
 _CUSTOMIZATION_EPOCH,
 0,
 0)
_EMPTY_INSCRIPTIONS = (_EMPTY_INSCRIPTION,
 _EMPTY_INSCRIPTION,
 _EMPTY_INSCRIPTION,
 _EMPTY_INSCRIPTION)
_EMPTY_CAMOUFLAGE = (None, _CUSTOMIZATION_EPOCH, 0)
_EMPTY_CAMOUFLAGES = (_EMPTY_CAMOUFLAGE, _EMPTY_CAMOUFLAGE, _EMPTY_CAMOUFLAGE)
_RANGE_4 = range(4)
_RANGE_OPTIONAL_DEVICE_SLOTS = range(NUM_OPTIONAL_DEVICE_SLOTS)
_VEHICLE = items.ITEM_TYPES['vehicle']
_CHASSIS = items.ITEM_TYPES['vehicleChassis']
_TURRET = items.ITEM_TYPES['vehicleTurret']
_GUN = items.ITEM_TYPES['vehicleGun']
_ENGINE = items.ITEM_TYPES['vehicleEngine']
_FUEL_TANK = items.ITEM_TYPES['vehicleFuelTank']
_RADIO = items.ITEM_TYPES['vehicleRadio']
_TANKMAN = items.ITEM_TYPES['tankman']
_OPTIONALDEVICE = items.ITEM_TYPES['optionalDevice']
_SHELL = items.ITEM_TYPES['shell']
_EQUIPMENT = items.ITEM_TYPES['equipment']
