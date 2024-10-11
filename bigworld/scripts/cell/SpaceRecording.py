"""
This module holds functions that are intended to be imported into the CellApp
personality script in order to implement space recording.

e.g.

from SpaceRecording import onRecordingTickData
"""

import BigWorld
from bwdecorators import eventListener

import cPickle

SPACE_DATA_RECORDER_FRAGMENT = BigWorld.SPACE_DATA_FIRST_CELL_ONLY_KEY + 1024

import logging
log = logging.getLogger( "Recorder" )


def recordersForSpaceID( spaceID ):
	"""
	This method returns a list of mailboxes to the SpaceRecorder instances for
	the given space, or None if no such instance is known.

	@param spaceID 	The space ID.
	@return 		A mailbox to the SpaceRecorder instance, or None.
	"""
	try:
		recordersPickle = BigWorld.getSpaceDataFirstForKey( spaceID, 
			SPACE_DATA_RECORDER_FRAGMENT )
		return cPickle.loads( recordersPickle )
	except:
		return []


@eventListener( "onRecordingTickData" )
def onRecordingTickData( spaceID, gameTime, name, numCells, blob ):
	"""
	This module callback method is called when space recording has been ticked.

	@param spaceID 		The space ID.
	@param gameTime 	The game time in ticks for the tick data.
	@param name 		The name of the recording.
	@param numCells 	The number of cells in the space (and so, other
						expected tick data blobs).
	@param blob			The recording data blob.
	"""

	recorders = recordersForSpaceID( spaceID )

	if not recorders:
		# We have no recorders. The recording space data may have been 
		# auto-loaded, so we should just clean up here.
		log.info( "onRecordingTickData: "
			"Stopping recording due to lack of recorders" )
		BigWorld.stopRecording( spaceID )

	for recorder in recorders:
		recorder.cellTickData( spaceID, gameTime, numCells, blob )

@eventListener( "onRecordingStarted" )
def onRecordingStarted( spaceID, blob ):
	log.debug( "onRecordingStarted: "
			"Startted recording on space: %d", spaceID )

# SpaceRecording.py

