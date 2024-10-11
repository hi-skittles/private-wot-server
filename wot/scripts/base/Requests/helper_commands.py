import cPickle
from itertools import cycle

import json
import os
import ResMgr

import AccountCommands
import items
from bwdebug import DEBUG_MSG
from items import ITEM_TYPE_INDICES, vehicles

class InventoryManager:
	
	def __init__(self):
		directory = ResMgr.resolveToAbsolutePath('scripts/db/inventory')
		self.filepath = directory
		if not os.path.exists(directory):
			os.makedirs(directory)
	
	def get_inventory(self, databaseID):
		"""Reads the inventory from a JSON file for a specific user."""
		DEBUG_MSG('InventoryManager : get_inventory=%s' % databaseID)
		filename = os.path.join(self.filepath, "%s.pickle" % databaseID)
		
		if not os.path.isfile(filename):
			return self.__initEmptyInventory(databaseID)
		
		with open(filename, 'rb') as file:
			data = cPickle.load(file)
		
		return data
	
	def init_empty_inventory(self, databaseID):
		"""Initializes an empty inventory and writes it to a JSON file."""
		DEBUG_MSG('InventoryManager : init_empty_inventory=%s' % databaseID)
		return self.__initEmptyInventory(databaseID)
	
	def set_inventory(self, databaseID, data):
		"""Writes the inventory to a JSON file for a specific user."""
		DEBUG_MSG('InventoryManager : set_inventory=%s' % databaseID)
		filename = os.path.join(self.filepath, "%s.pickle" % databaseID)
		
		with open(filename, 'wb') as file:
			cPickle.dump(data, file)
	
	def __initEmptyInventory(self, databaseID):
		"""Initializes an empty inventory and writes it to a JSON file."""
		DEBUG_MSG('InventoryManager : __initEmptyInventory=%s' % databaseID)
		data = dict((k, {}) for k in ITEM_TYPE_INDICES)
		i = 1
		i_crew = 1
		compDescr = {}
		
		data['customizations'] = {
			False: {},
			True: {}
		}
		
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
		
		for value in vehicles.g_list._VehicleList__ids.values():
			if value == (0, 0) or value == (5, 210):
				vehicle = vehicles.VehicleDescr(typeID=value)
				compDescr[i] = vehicle.makeCompactDescr()
				turretGun = (
					vehicles.makeIntCompactDescrByID('vehicleTurret', *vehicle.turrets[0][0]['id']),
					vehicles.makeIntCompactDescrByID('vehicleGun', *vehicle.turrets[0][0]['guns'][0]['id'])
				)
				
				tmanList = items.tankmen.generateTankmen(value[0], value[1], vehicle.type.crewRoles, False,
				                                         items.tankmen.MAX_SKILL_LEVEL, [])
				tmanListCycle = cycle(tmanList)
				
				data[ITEM_TYPE_INDICES['vehicle']]['crew'].update({i: [tmanID for tmanID in range(i_crew, len(tmanList) + i_crew)]})
				data[ITEM_TYPE_INDICES['vehicle']]['settings'].update({i: AccountCommands.VEHICLE_SETTINGS_FLAG.AUTO_REPAIR | AccountCommands.VEHICLE_SETTINGS_FLAG.AUTO_LOAD})
				data[ITEM_TYPE_INDICES['vehicle']]['compDescr'].update(compDescr)
				data[ITEM_TYPE_INDICES['vehicle']]['eqs'].update({i: []})
				data[ITEM_TYPE_INDICES['vehicle']]['eqsLayout'].update({i: []})
				# data[ITEM_TYPE_INDICES['vehicle']]['shells'].update({i: vehicles.getDefaultAmmoForGun(vehicle.turrets[0][0]['guns'][0])})
				data[ITEM_TYPE_INDICES['vehicle']]['shellsLayout'].update({i: {turretGun: vehicles.getDefaultAmmoForGun(vehicle.turrets[0][0]['guns'][0])}})
				
				for tmanID in range(i_crew, len(tmanList) + i_crew):
					data[ITEM_TYPE_INDICES['tankman']]['vehicle'][tmanID] = i
					data[ITEM_TYPE_INDICES['tankman']]['compDescr'][tmanID] = next(tmanListCycle)
					i_crew += 1
				
				i += 1
		
		rdata = {'inventory': data}
		
		self.set_inventory(databaseID, rdata)
		return rdata
	

def __returnPremiumPrices():
	return {
		1: 250,
		3: 650,
		7: 1250,
		360: 26000,
		180: 13500,
		30: 2500
	}

def __returnCreditsPrice():
	return 400