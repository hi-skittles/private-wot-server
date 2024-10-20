from bwdebug import DEBUG_MSG, ERROR_MSG
from constants import ACCOUNT_ATTR
import time

from db_scripts.responders.ShopHandler import premiumPrices, creditsPrice, slotsPrices, freeXPRate
from items import vehicles, ITEM_TYPE_INDICES
from debug_utils import LOG_CURRENT_EXCEPTION

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
# economics :: eliteVehicles
# inventory :: 1 (tanks) :: compDescr, crew, eqs, eqsLayout, settings, shellsLayout
# inventory :: 8 (crew) :: compDescr, vehicle
def __buyVehicle(data, shopRev, vehTypeCompDescr, int1, int2, int3):
    pass

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