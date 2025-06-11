"""
This script is to schedule tasks that will run regularly within WebConsole
"""

import os
import logging
import time

from turbogears import config
from turbogears import scheduler

log = logging.getLogger( __name__ )

# schedule tasks, this function will be called during server startup
def scheduleTasks():	
	uploadDir = config.get( 'web_console.upload_directory' )

	maxDays = config.get( 'web_console.upload_dir_max_days' )
	if not maxDays or maxDays <= 0:
		maxDays = 30

	maxSizeInMB = config.get( 'web_console.upload_dir_max_size' )
	if not maxSizeInMB or maxSizeInMB <= 0:
		maxSizeInMB = 2048

	# transform the size unit from GB to byte
	maxSize = maxSizeInMB * 1024 * 1024

	scheduledTimeStr = config.get( 'web_console.upload_dir_clean_time' )
	try:
		scheduledTime = time.strptime( scheduledTimeStr, "%H:%M:%S" )
	except Exception:
		log.error( "Invalid schedule time: %s.", scheduledTimeStr )
		raise
		
	initialDelay, interval = getInitialDelayAndInterval( scheduledTime )	
	log.info( "Scheduling cleaning up upload directory task, " \
		"uploadDir:%s, maxDays: %d, maxSize: %d, scheduledTime:%s, " \
		"initialDelay:%d, interval:%d", 
		uploadDir, maxDays, maxSize, scheduledTimeStr, initialDelay, interval )

	# Schedule the task to clean up upload directory
	# add_weekday_task seems to be more proper but has an issue in Tubogears 1.0
	# so we use add_interval_task instead
	scheduler.add_interval_task( action = cleanUploadDir,
								taskname = 'cleanUploadDir',
								initialdelay = initialDelay,
								interval = interval,
								args = [ uploadDir, maxDays, maxSize ] )
# schedule


def getInitialDelayAndInterval( scheduledTime ):
	initialDelay = 0

	import time
	currentTime = time.localtime()

	currentSecondsOfDay = \
		( currentTime.tm_hour * 60 + currentTime.tm_min ) * 60 \
		+ currentTime.tm_sec

	scheduledSecondsOfDay = \
		( scheduledTime.tm_hour * 60 + scheduledTime.tm_min ) * 60 \
		+ scheduledTime.tm_sec

	initialDelay = scheduledSecondsOfDay - currentSecondsOfDay	
	if initialDelay < 0:
		initialDelay += 24 * 60 * 60

	return ( initialDelay, 24 * 60 * 60 )


# clean up upload directory by deleting expired files
def cleanUploadDir( uploadDir, maxDays, maxSize ):	
	log.info( 'Clean upload director task is launched,'  \
				'directory:%s, maxDays:%s, maxSize:%d',
				uploadDir, maxDays, maxSize )

	remainingFiles = []
	remainingSize = deleteExpiredFiles( uploadDir, maxDays, remainingFiles )

	if remainingSize > maxSize:
		deleteFilesToFreeDisk( remainingFiles, remainingSize, maxSize )
# cleanUploadDir


# delete expired file under specified directory
def deleteExpiredFiles( dirToClean, maxDays, remainingFiles ):
	remainingSize = 0
	for entry in os.listdir( dirToClean ):
		entryPath = os.path.join( dirToClean, entry )
		if os.path.isdir( entryPath ):
			# recursively clean sub directories
			remainingSize += deleteExpiredFiles( entryPath, maxDays,
									remainingFiles )
		elif os.path.isfile( entryPath ):
			fileStat = os.stat( entryPath )				
			mTime = fileStat.st_mtime 
			existingDays = ( time.time() - mTime ) / ( 24 * 60 * 60 )

			# delete expired file
			if existingDays > maxDays:
				os.remove( entryPath )
				log.info( 'Deleted expired file: %s' % entryPath )

				deleteDirIfEmpty( os.path.dirname( entryPath ) )
			else:
				remainingSize += fileStat.st_size

				fileInfo = FileInfo( entryPath, fileStat.st_mtime, 
								fileStat.st_size )
				remainingFiles.append( fileInfo )
	
	return remainingSize
# deleteExpiredFiles


def deleteFilesToFreeDisk( fileInfoList, currentSize, maxSize ):
	# sort the file info list by modify time in ascending order
	import operator
	fileInfoList.sort( key = operator.attrgetter( 'modifyTime' ) )

	while currentSize > maxSize:
		oldestFile = fileInfoList.pop( 0 )

		os.remove( oldestFile.fullPath )
		currentSize -= oldestFile.size
		log.info( 'Deleted file to free disk space: %s' % oldestFile.fullPath )

		deleteDirIfEmpty( os.path.dirname( oldestFile.fullPath ) )
# deleteFilesToFreeDisk


def deleteDirIfEmpty( dirPath ):
	if not os.listdir( dirPath ):
		os.rmdir( dirPath )
		log.info( 'Removed empty directory: %s', dirPath )
	
		
class FileInfo( object ):
	def __init__( self, fullPath, modifyTime, size ):
		self.fullPath = fullPath
		self.modifyTime = modifyTime
		self.size = size
# class FileInfo

