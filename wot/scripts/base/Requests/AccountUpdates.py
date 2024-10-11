import items
from bwdebug import DEBUG_MSG
from constants import ACCOUNT_ATTR
import helper_commands
import time

from db_scripts.responders.ShopHandler import premiumPrices, creditsPrice
from items import vehicles

vehicle_prices = {}
items_prices = {}
items.init(True, items_prices)
vehicles.init(True, vehicle_prices)
global vehicle_prices
global items_prices

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


def __exchangeGold(currency, data, use_gold=True, isCredits=True):
	new_gold_balance = data['stats']['gold'] - currency
	if new_gold_balance < 0 and use_gold:
		return -1, 'Not enough gold', None
	
	if isCredits:
		DEBUG_MSG('AccountCommands.CMD_EXCHANGE :: credits exchange')
		if use_gold: data['stats']['gold'] -= currency
		data['stats']['credits'] += currency * creditsPrice
		return 2, 'Credits exchanged', data
	else:
		# FreeXP - not used until we make tanks earn XP
		DEBUG_MSG('AccountCommands.CMD_FREE_XP_CONV :: freeXP exchange')
		if use_gold: data['stats']['gold'] -= currency
		data['stats']['freeXP'] += currency
		return 2, 'FreeXP exchanged', data