"This module implements some utility methods."

import BigWorld
import Avatar
#import Creature
#import Guard
import random

def broadcast( msg ):
	# Note: Only on the local CellApp.
	for e in entitiesOfType( "Avatar" ):
		if e.isReal():
			e.client.chat( unicode(msg) )

def findPlayer(playerName):
	for entity in BigWorld.entities.values():
		if entity.__class__ == Avatar.Avatar and entity.playerName == playerName:
			return entity


SPAWN_RADIUS = 10
SPAWN_COUNT = 10

def spawnStriffs(id, spaceID = 1):
	dict = {"creatureType" : 1}
	pos = BigWorld.entities[id].position

	for i in range(SPAWN_COUNT):
		x = pos[0] + random.random() * SPAWN_RADIUS * 2 - SPAWN_RADIUS;
		z = pos[2] + random.random() * SPAWN_RADIUS * 2 - SPAWN_RADIUS;
		#e = BigWorld.createEntity("Creature", spaceID, (x,0,z), (0, 0, 0), dict)

def spawnOrcs(id, spaceID = 1):
	dict = {"modelNumber" : 8, "aggro" : 1, "playerName" : u"Orc"}
	pos = BigWorld.entities[id].position

	for i in range(SPAWN_COUNT):
		x = pos[0] + random.random() * SPAWN_RADIUS * 2 - SPAWN_RADIUS;
		z = pos[2] + random.random() * SPAWN_RADIUS * 2 - SPAWN_RADIUS;
		dict["rightHand"] = 8
#	dict["rightHand"] = random.randrange(0,2)
#		e = BigWorld.createEntity("Guard", spaceID, (x,0,z), (0, 0, 0), dict)

def spawnGuards(id, spaceID = 1):
	dict = {"modelNumber" : 6, "aggro" : 1, "playerName" : u"Guard"}
	pos = BigWorld.entities[id].position

	for i in range(SPAWN_COUNT):
		x = pos[0] + random.random() * SPAWN_RADIUS * 2 - SPAWN_RADIUS;
		z = pos[2] + random.random() * SPAWN_RADIUS * 2 - SPAWN_RADIUS;
		dict["rightHand"] = random.randrange(0,2)
#		e = BigWorld.createEntity("Guard", spaceID, (x,0,z), (0, 0, 0), dict)

def killSpawnedEntities():
	for id in filter(lambda x: x >= (1 << 24), BigWorld.entities.keys()):
		BigWorld.entities[id].destroy()

def killAllOfClass(name):
	for x in filter(lambda x, c = name: x.__class__ == c , BigWorld.entities.values()):
		x.destroy()

def entitiesOfType( t ):
	return [e for e in BigWorld.entities.values() if e.className == t]

def botsToOrcs():
	for entity in BigWorld.entities.values():
		if entity.id > 1000 and entity.id < 2000:
			entity.playerName = "Orc"
			entity.modelNumber = 8
			entity.rightHand = 7

#def stealStriff():
#	for entity in BigWorld.entities.values():
#		if entity.__class__ == Creature.Creature:
#			entity.ownerId = 1

def lowHealth():
	for entity in BigWorld.entities.values():
		if entity.__class__ == Avatar.Avatar:
			entity.health = 10
			entity.maxHealth = 10

# Note: Navigate will not work if the destination is in a chunk
# that has not been loaded yet. Keep distances smaller than chunk
# size, and this will be fine.

def offset(radius):
	return random.randrange(-radius/2, radius/2)

def addGuards(count, dict, path, radius, spaceID = 1):
	for i in range(count):
		path2 = []
		path3 = []

		for p in path:
			point = (p[0] + offset(radius), p[1], p[2] + offset(radius))
			path2.append(point)
			path3.append("%f %f %f" % point)

		dict["patrolList"] = path3
		n = random.randrange(len(path))
		dict["initialWait"] = random.uniform(5.0, 30.0)
#		BigWorld.createEntity("Guard", spaceID, path2[n], (0,0,0), dict)

def smite(playerName):
	player = findPlayer(playerName)
	if player:
		for entity in BigWorld.entities.values():
			if entity.__class__ == Guard.Guard:
				entity.hate(player.id, 1.0)


def patrollingGuards( count, modelNumber = 3, radius = 2.0, spaceID = 1):
#	dict = {"modelNumber" : modelNumber , "playerName" : "Guard",
#	}
	path = [(-222.104446, -0.685044, 0.482476),
			(-208.377472, 0.130510, 6.725818),
			(-187.788055, -0.727536, 9.066783),
			(-167.625488, 0.627261, 11.362390),
			(-149.872925, 1.224653, 11.629924),
			(-127.675102, -2.200806, 9.125811),
			(-102.751030, -4.763248, 8.359866),
			(-82.182083, -2.876489, 7.947742),
			(-62.860512, -0.938930, 8.361094),
			(-40.962639, 0.000000, 8.214519),
			(-14.744971, 0.014050, 11.718305)
	]
	for i in range(count):
		path2 = []
		path3 = []

		for p in path:
			point = (p[0] + offset(radius), p[1], p[2] + offset(radius))
			path2.append(point)
			path3.append("%f %f %f" % point)

		dict["patrolList"] = path3
		dict["rightHand"]  = random.choice([-1, 0, 1, 8])
		n = random.randrange(len(path))
		dict["initialWait"] = random.uniform(5.0, 15.0)
#		BigWorld.createEntity("Guard", spaceID, path2[n], (0,0,0), dict)

# util.py
