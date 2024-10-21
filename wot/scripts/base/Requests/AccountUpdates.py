import traceback
from itertools import cycle

import AccountCommands
import items
from bwdebug import DEBUG_MSG, ERROR_MSG
from constants import ACCOUNT_ATTR
import time

from db_scripts.responders.ShopHandler import premiumPrices, creditsPrice, slotsPrices, freeXPRate
from items import vehicles, ITEM_TYPE_INDICES
from debug_utils import LOG_CURRENT_EXCEPTION
from wot import vehicle_prices

slotsPrices = slotsPrices[1][0]
freeXPRate = freeXPRate[0]

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
def subtract_want_equally(want, values):
    n = len(values)
    
    # check if it's possible to subtract want from the sum of values
    if sum(values) < want:
        raise ValueError("The total sum of the array is less than 'want', operation not possible.")
    
    # calculate the equal part to subtract from each element
    equal_part = want // n
    remainder = want % n
    print equal_part, remainder
    
    # create a copy of the array to avoid modifying the original one
    new_values = values[:]
    
    # subtract the equal part from each element
    for i in range(n):
        if new_values[i] < equal_part:  # Val-add | Preventing negative values
            remainder += equal_part - new_values[i]
            new_values[i] = 0
            continue
        
        new_values[i] -= equal_part
    
    # subtract the remainder from the first element (could be any, doesn't matter)
    for i in range(n):
        if new_values[i] >= remainder:
            new_values[i] -= remainder
            break
    
    return new_values

####

# stats :: gold, maxResearchedLevelByNation, slots, vehTypeXP, unlocks
# stats :: economics :: eliteVehicles
# inventory :: 1 (tanks) :: compDescr, crew, eqs, eqsLayout, settings, shellsLayout
# inventory :: 8 (crew) :: compDescr, vehicle
def __buyVehicle(s_data, i_data, shopRev, vehTypeCompDescr, int1, int2, int3):
    if int2 != -1 or int3 != -1:
        return -1, 'Crew NYI', s_data, i_data
    
    orig_s_data = s_data.copy()
    orig_i_data = i_data.copy()
    
    notInShopItems = vehicle_prices['notInShopItems']
    if vehicle_prices['itemPrices'].get(vehTypeCompDescr) and vehTypeCompDescr not in notInShopItems:
        try:
            tank = vehicles.getVehicleType(vehTypeCompDescr)   # should always be true?
        except KeyError as e:
            ERROR_MSG("AccountCommands.CMD_BUY_VEHICLE :: Failed to get tank data -", e)
            return -1, 'Failed to get tank from shop', s_data, i_data
        gold = s_data['stats']['gold']
        credits = s_data['stats']['credits']
        max_res_level = s_data['stats']['maxResearchedLevelByNation']
        slots = s_data['stats']['slots']
        veh_xp = s_data['stats']['vehTypeXP']
        unlocks = s_data['stats']['unlocks']
        vehicle_price = vehicle_prices['itemPrices'].get(vehTypeCompDescr)
    else:
        return -1, 'Tank not found in prices or is not available for purchase', s_data, i_data
    
    if len(i_data['inventory'].get(1).get('compDescr')) + 1 > slots:
        return -1, 'Not enough slots. Purchase another slot when buying tank', s_data, i_data
    
    if gold < vehicle_price[1] or credits < vehicle_price[0]:
        return -1, 'Not enough resources', s_data, i_data
    
    s_data['stats']['credits'] -= vehicle_price[0]
    s_data['stats']['gold'] -= vehicle_price[1]

    try:
        value = vehicles.getVehicleType(vehTypeCompDescr).id
        tank_nation_id, tank_id = value[0], value[1]
        vehicle = vehicles.VehicleDescr(typeID=value)
        newCompDescr = vehicle.makeCompactDescr()
        
        i = len(i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['compDescr']) + 1
        i_crew = len(i_data['inventory'][ITEM_TYPE_INDICES['tankman']]['compDescr']) + 1
        
        turretGun = (vehicles.makeIntCompactDescrByID('vehicleTurret', *vehicle.turrets[0][0]['id']),
                     vehicles.makeIntCompactDescrByID('vehicleGun', *vehicle.turrets[0][0]['guns'][0]['id']))
        
        tmanList = items.tankmen.generateTankmen(value[0], value[1], vehicle.type.crewRoles, True,
                                                 items.tankmen.MAX_SKILL_LEVEL, [])
        tmanListCycle = cycle(tmanList)
        
        i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['crew'].update(list())    # {i: [tmanID for tmanID in xrange(i_crew, len(tmanList) + i_crew)]}
        i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['settings'].update(
            {i: AccountCommands.VEHICLE_SETTINGS_FLAG.AUTO_REPAIR | AccountCommands.VEHICLE_SETTINGS_FLAG.AUTO_LOAD})
        i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['compDescr'].update({i: newCompDescr})
        i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['eqs'].update({i: []})
        i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['eqsLayout'].update({i: []})
        i_data['inventory'][ITEM_TYPE_INDICES['vehicle']]['shellsLayout'].update(
            {i: {turretGun: vehicles.getDefaultAmmoForGun(vehicle.turrets[0][0]['guns'][0])}})
        
        # for tmanID in xrange(i_crew, len(tmanList) + i_crew):
        #     i_data['inventory'][ITEM_TYPE_INDICES['tankman']]['vehicle'][tmanID] = i
        #     i_data['inventory'][ITEM_TYPE_INDICES['tankman']]['compDescr'][tmanID] = next(tmanListCycle)
        #     i_crew += 1
        
        s_data['stats']['vehTypeXP'].update({newCompDescr: 0}) if newCompDescr not in veh_xp else None
        
        for i in vehicles.getVehicleType(vehTypeCompDescr).autounlockedItems:
            s_data['stats']['unlocks'].add(i) if i not in unlocks else None
            
        if 'premium' in tank.tags:
            s_data['stats']['eliteVehicles'] = set([vehTypeCompDescr])
            s_data['economics']['eliteVehicles'].add(vehTypeCompDescr)
        
        if max_res_level.get(tank_nation_id) < tank.level:
            s_data['stats']['maxResearchedLevelByNation'][tank_nation_id] = tank.level
        
        return 2, 'Tank bought', s_data, i_data
    except Exception:
        ERROR_MSG("AccountCommands.CMD_BUY_VEHICLE :: Failed to buy tank -", traceback.format_exc())
        return -1, 'Failed to buy tank', orig_s_data, orig_i_data

#   stats :: gold, slots
def __buySlot(data):
    if data['stats']['gold'] < slotsPrices:
        return -1, 'Not enough gold', None
    data['stats']['gold'] -= slotsPrices
    data['stats']['slots'] += 1
    return 2, 'Slot bought', data

#   stats :: vehTypeXP, freeXP, unlocks
def __unlockItem(vehTypeCompDescr, unlockIdx, data):
    try:
        print "AccountCommands.CMD_UNLOCK :: begin", vehTypeCompDescr, unlockIdx
        vehicleType = vehicles.getVehicleType(vehTypeCompDescr)
        itemToUnlock = f7(vehicleType.unlocksDescrs)[unlockIdx]
        xpCost, itemCD = itemToUnlock[0], itemToUnlock[1]
        vehXp = data['stats']['vehTypeXP'][vehTypeCompDescr]
        freeXp = data['stats']['freeXP']
        if itemCD in data['stats']['unlocks']:
            return -1, 'Item already unlocked', data  # eof
        elif vehXp >= xpCost:  # have enough research xp
            data['stats']['vehTypeXP'][vehTypeCompDescr] -= xpCost
        elif vehXp <= xpCost <= (freeXp + vehXp):  # veh xp could be zero, doesn't matter
            cost_after_veh_xp = xpCost - vehXp  # we want to use vehXP first, even if it's zero, this still works properly
            data['stats']['vehTypeXP'][vehTypeCompDescr] = 0  # they've used all of their remaining vehXP anyways
            if freeXp >= cost_after_veh_xp:  # should always be true
                data['stats']['freeXP'] -= cost_after_veh_xp  # subtract remaining cost from freeXP
            else:
                return -1, 'Not enough tankXP or freeXP', data
        else:
            return -1, 'Not enough tankXP or freeXP', data
        
        data['stats']['unlocks'].add(itemCD)
        
        if itemCD not in vehicleType.installableComponents:
            for i in vehicles.getVehicleType(itemCD).autounlockedItems:
                data['stats']['unlocks'].add(i)
                data['stats']['vehTypeXP'][itemCD] = 0
        
        unlocksItemsCD = [i[1] for i in f7(vehicleType.unlocksDescrs)]
        unlocked_count = 0
        
        for unlock in data['stats']['unlocks']:
            if len(unlocksItemsCD) == unlocked_count:
                break
            if unlock in unlocksItemsCD:
                unlocked_count += 1
        
        if unlocked_count == len(unlocksItemsCD):
            data['stats']['eliteVehicles'] = set([vehTypeCompDescr])
            data['economics']['eliteVehicles'].add(vehTypeCompDescr)
        
        return 2, 'Item unlocked', data
    except Exception as e:
        DEBUG_MSG("AccountCommands.CMD_UNLOCK :: Failed to unlock item -", vehTypeCompDescr, unlockIdx, str(e))
        return -1, 'Unexcepted error', data


#   stats :: gold
#   account :: premiumExpiryTime, attrs
def __addPremiumTime(extend_by_days, data, use_gold=True):
    #   stats[gold] -= price
    #   account[premiumExpiryTime] += extend_by_days * 86400
    #   account[attrs] |= ACCOUNT_ATTR.PREMIUM w/ checks
    current_epoch = time.time()
    pcost = premiumPrices[extend_by_days]
    new_gold_balance = data['stats']['gold'] - pcost
    if new_gold_balance < 0 and use_gold:
        return -1, 'Not enough gold', None
  
    attrs = data['account']['attrs']
    # remove value from attr: attrs &= ~value
    # check attr for value: attrs & value
    if attrs & ACCOUNT_ATTR.PREMIUM:
        DEBUG_MSG('AccountCommands.CMD_PREMIUM :: already premium')
        if use_gold: data['stats']['gold'] -= pcost
        if data['account']['premiumExpiryTime'] < current_epoch:    # was expired
            data['account']['premiumExpiryTime'] = (extend_by_days * 86400) + current_epoch
        else:   # not expired
            data['account']['premiumExpiryTime'] += extend_by_days * 86400
        return 2, 'Premium extended', data
    else:
        DEBUG_MSG('AccountCommands.CMD_PREMIUM :: not already premium')
        if use_gold: data['stats']['gold'] -= pcost
        if data['account']['premiumExpiryTime'] < current_epoch:    # they have had premium in the past; and we have no functionality to set it back to zero after it expires.
            data['account']['premiumExpiryTime'] = (extend_by_days * 86400) + current_epoch
        else:
            data['account']['premiumExpiryTime'] += (extend_by_days * 86400) + current_epoch
        data['account']['attrs'] |= ACCOUNT_ATTR.PREMIUM
        return 1, 'Premium activated', data


#   stats :: gold, credits
def __exchangeGold(currency, data):
    new_gold_balance = data['stats']['gold'] - currency
    if new_gold_balance < 0:
        return -1, 'Not enough gold', None
    
    DEBUG_MSG('AccountCommands.CMD_EXCHANGE :: credits exchange')
    data['stats']['gold'] -= currency
    data['stats']['credits'] += currency * creditsPrice
    return 2, 'Credits exchanged', data


#   stats :: gold, credits
def __giveGoldWatcher(add, data):
    DEBUG_MSG('AccountCommands.CMD_EXCHANGE :: credits exchange')
    data['stats']['gold'] += add
    return 2, '', data


def __exchangeFreeXP(wantedXP, data, vehTypeDesrcs):
    try:
        gold_to_use = wantedXP / freeXPRate
        new_gold_balance = data['stats']['gold'] - gold_to_use
        if new_gold_balance < 0:
            return -1, 'Not enough gold', None
        
        if 65281 not in vehTypeDesrcs:  # Observer in dict -> freeXP convert without any elite tanks XP -> just take gold and give freeXP
            vehicleXPs = []
            for vehicle in vehTypeDesrcs:
                vehicleXPs.append(data['stats']['vehTypeXP'][vehicle])
            
            newVehicleXPs = subtract_want_equally(wantedXP, vehicleXPs)
            vehiclesDict = zip(vehTypeDesrcs, newVehicleXPs)
            
            for vehicle, xp in vehiclesDict:
                data['stats']['vehTypeXP'][vehicle] = xp
        
        DEBUG_MSG('AccountCommands.CMD_FREE_XP_CONV :: freeXP exchange')
        data['stats']['gold'] -= gold_to_use
        data['stats']['freeXP'] += wantedXP
        return 2, 'FreeXP exchanged', data
    except:
        LOG_CURRENT_EXCEPTION()
        return -1, 'Unexcepted error', None