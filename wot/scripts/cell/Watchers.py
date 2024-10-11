import BigWorld
import Math
import util

from bwdecorators import watcher, functionWatcher, functionWatcherParameter


def numInAoI():
	return float( BigWorld.getWatcher( "stats/numInAoI" ) )


def numWitnesses():
	return float( BigWorld.getWatcher( "stats/numWitnesses" ) )


@watcher( "python/avgAoI" )
def avgAoI():
	try:
		return numInAoI()/numWitnesses()
	except ZeroDivisionError:
		return 0


def getWatcherTime( entry ):
	return float( BigWorld.getWatcher( entry ) ) / \
		float( BigWorld.getWatcher( "stats/stampsPerSecond" ) )


@watcher( "python/updateClient" )
def updateClientTime():
	return getWatcherTime( "profiles/details/updateClient/sumTime" )


@watcher( "python/updateClientSend" )
def updateClientSendTime():
	return getWatcherTime( "profiles/details/updateClientSend/sumTime" )


@watcher( "python/runningTime" )
def runningTime():
	return getWatcherTime( "stats/runningTime" )


@watcher( "python/idleTime" )
def idleTime():
	return getWatcherTime( "nub/timing/totalSpareTime" )


@watcher( "python/busyTime" )
def busyTime():
	return runningTime() - idleTime()


@functionWatcher( "command/hasEntity",
		BigWorld.EXPOSE_CELL_APPS,
		"Check if the entity exists on a CellApp." )
@functionWatcherParameter( int, "Entity ID" )
def findEntity( id ):
	try:
		if BigWorld.entities.has_key( id ):
			e = BigWorld.entities[ id ]
			print "Entity[%s]: %s" % (id, str( e ))
			print " - Space   :", e.spaceID
			print " - Position:", e.position
			print " - isReal  :", e.isReal()
			return "I own this entity"
	except:
		pass

	return "Couldn't find entity", id


@functionWatcher( "command/entitiesOfType", 
		BigWorld.EXPOSE_CELL_APPS,
		"Count the number of entities of a given type." )
@functionWatcherParameter( str, "Name of Entity Type" )
def entitiesOfType( type ):
	return len( util.entitiesOfType( type ) )


@functionWatcher( "command/onlinePlayers",
		BigWorld.EXPOSE_CELL_APPS,
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


@functionWatcher( "command/teleportEntity",
		BigWorld.EXPOSE_CELL_APPS,
		"Teleport an entity to the requested position." )
@functionWatcherParameter( int, "Entity ID" )
@functionWatcherParameter( float, "X Position" )
@functionWatcherParameter( float, "Y Position" )
@functionWatcherParameter( float, "Z Position" )
def teleportEntity( id, x, y, z ):

	vector = Math.Vector3( x, y, z )

	if BigWorld.entities.has_key( id ):
		e = BigWorld.entities[ id ]
		if e.isReal():
			e.position = vector

			return "Teleported entity %d to %s" % (id, vector)

	return


def addWatchers():
	addPercent( "avatarUpdate" )
	addPercent( "ghostAvatarUpdate" )
	addPercent( "deliverGhosts" )
	addPercent( "boundaryCheck" )
	addPercent( "gameTick",     "1   " )
	addPercent( "calcBoundary", "1.1 " )
	addPercent( "callTimers",   "1.2 " )
	addPercent( "callUpdates",  "1.3 " )
	addPercent( "updateClient", "1.3.1 " )


class PercentageOfBusy( object ):
	def __init__( self, entry, prefix = "" ):
		self.name = "python/percent/" + prefix + entry
		self.profile = "profiles/details/" + entry + "/sumTime"

	def __call__( self ):
		t1 = getWatcherTime( self.profile )
		t2 = busyTime()
		return "%.4f" % (t1/t2,)


def addPercent( entry, prefix = "" ):
	watcher = PercentageOfBusy( entry, prefix )
	BigWorld.addWatcher( watcher.name, watcher )

