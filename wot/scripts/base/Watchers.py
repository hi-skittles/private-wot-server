import cPickle

import BigWorld
import util
import traceback
from bwdecorators import functionWatcher, functionWatcherParameter

from Requests import AccountUpdates
from bwdebug import DEBUG_MSG

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


# Add premium time in days to given player
# -----------------------------------------------------------------------------
# @functionWatcher( "command/wot:AddPremium",
# 		BigWorld.EXPOSE_BASE_APPS,
# 		"WoT: Adds premium time to player, in days" )
# @functionWatcherParameter(int, "Player's EntityID")
# @functionWatcherParameter(int, "Days")
# def addPremiumTime(entID, days):
# 	playerProxy = BigWorld.entities[entID]
# 	rdata = Helper.get_stats(playerProxy.databaseID)
# 	result, msg, udata = AccountUpdates.__addPremiumTime(days, rdata, False)
# 	if result > 0:
# 		print msg
# 		Helper.set_stats(playerProxy.databaseID, udata)
# 		udata.update({'rev': 1, 'prevRev': 0})
# 		playerProxy.ownClient.update(cPickle.dumps(udata))
# 	else:
# 		print msg



@functionWatcher( "command/onlinePlayers",
		BigWorld.EXPOSE_BASE_APPS,
		"Display the players that are online." )
def onlinePlayers():
	players = [p for p in util.entitiesOfType( "Avatar" ) if p.isReal()]

	if players:
		print "%-6s | %-10s | %-3s" % ("ID", "Name", "Space ID")
		print '------------------------------'
		for e in players:
			print "%6d | %-10s | %3s" % (e.id, e.playerName, e.spaceID)

	numPlayers = len( players )
	return "%d player%s" % (numPlayers, 's' if numPlayers != 1 else '')


# Watchers.py