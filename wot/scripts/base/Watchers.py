import cPickle

import BigWorld
import util
import traceback
from bwdecorators import functionWatcher, functionWatcherParameter
from adisp import async, process

from Requests import AccountUpdates
from bwdebug import DEBUG_MSG
from db_scripts.responders import StatsHandler


#import XMPPEventNotifier

# Kick player
# -----------------------------------------------------------------------------
@functionWatcher( "command/wot:KickPlayer",
		BigWorld.EXPOSE_BASE_APPS,
		"WoT: Kick player from game" )
@functionWatcherParameter(int, "Entity ID")
@functionWatcherParameter(str, "Reason")
def kickPlayerReturnMessage( entityID, reason ):
	try:
		# Better way -> Does entityID exist? Are we not out of range? After that kick
		BigWorld.entities[entityID].ownClient.onKickedFromServer(reason, False, 500)
		return "Successfully kicked player."
	except:
		traceback.print_exc()
		return "Failed to kick player."


# Find entityID from player's name
# -----------------------------------------------------------------------------
@functionWatcher( "command/wot:EntityIndexFromName",
		BigWorld.EXPOSE_BASE_APPS,
		"WoT: Returns entityID from player's name" )
@functionWatcherParameter(str, "Player's Name")
def getEntIDFromName(name):
	try:
		for idx, entity in BigWorld.entities.items():
			if entity.name == name:
				return idx
		else:
			return "Player not found."
	except:
		traceback.print_exc()
		return "Failed to get Player's EntityID."


# Add gold to given player
# -----------------------------------------------------------------------------
@functionWatcher( "command/wot:AddGold",
		BigWorld.EXPOSE_BASE_APPS,
		"WoT: Give gold to player" )
@functionWatcherParameter(str, "Player Name")
@functionWatcherParameter(int, "Gold")
@process
def addGold(name, gold):
	entityx = None
	try:
		for idx, entity in BigWorld.entities.items():
			if entity.name == name:
				entityx = entity
	except:
		traceback.print_exc()
		print "Failed to get Player's EntityID."
		return
	
	rdata = yield async(StatsHandler.get_stats, cbname='callback')(entityx.databaseID)
	result, msg, udata = AccountUpdates.__giveGoldWatcher(gold, rdata)
	
	cdata = {'rev': 1, 'prevRev': 0, 'stats': {'gold': None}}
	
	if result > 0:
		print('AccountCommands.CMD_EXCHANGE :: success=%s' % result)
		cdata['stats']['gold'] = udata['stats']['gold']
		
		entityx.client.update(cPickle.dumps(cdata))
		yield async(StatsHandler.update_stats, cbname='callback')(entityx.databaseID, udata)
		return
	else:
		print('AccountCommands.CMD_EXCHANGE :: failure=%s' % result)
		return


@functionWatcher( "command/onlinePlayers",
		BigWorld.EXPOSE_BASE_APPS,
		"Display the players that are online." )
def onlinePlayers():
	players = [p for p in util.entitiesOfType("Account")]

	if players:
		print "%-6s | %-10s | %-3s" % ("ID", "Name", "Space ID")
		print '------------------------------'
		for e in players:
			print "%6d | %-10s | %3s" % (e.id, e.playerName, None)

	numPlayers = len( players )
	return "%d player%s" % (numPlayers, 's' if numPlayers != 1 else '')


# Watchers.py