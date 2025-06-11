
# Turbogears stuff
from turbogears import identity, config
import cherrypy
import logging
import simplejson as json

log = logging.getLogger( __name__ )

from pycommon.exceptions import ConfigurationException


class UserFeedback( object ):

	def __init__( self ):
		self._readConfig()
	# __init__


	def _readConfig( self ):
		# WebConsole User Feedback configuration
		self.isEnabled = config.get(
			'web_console.user_feedback.enabled', False )

		# Initialise variables in case they are accessed when not enabled
		self.toAddressList = []
		self.smtpHost = ""
		self.smtpPort = 0
		self.fromAddress = ""
		self.authLogin = ""
		self.authPassword = ""

		if self.isEnabled:
			log.info( "Loading user feedback configuration" )

			emailAddresses = \
				config.get( 'web_console.user_feedback.to_addresses', '' )

			# Simple split by semicolon and optionally whitespace
			import re
			self.toAddressList = re.split( r"\s*;\s*", emailAddresses.strip() )

			if not self.toAddressList:
				errMessage = "Configuration error: No " \
					"web_console.user_feedback.to_addresses provided"
				log.error( errMessage )
				raise ConfigurationException, errMessage


			self.smtpHost = config.get( 'web_console.user_feedback.smtp_host',
				'' )

			if not self.smtpHost:
				errMessage = "Configuration error: No " \
					"web_console.user_feedback.smtp_host provided."
				log.error( errMessage )
				raise ConfigurationException, errMessage

			self.smtpPort = config.get( 'web_console.user_feedback.smtp_port',
				'' )

			if not self.smtpPort:
				errMessage = "Configuration error: No " \
					"web_console.user_feedback.smtp_port provided."
				log.error( errMessage )
				raise ConfigurationException, errMessage

			self.fromAddress = config.get(
				'web_console.user_feedback.from_address', '' )

			if not self.fromAddress:
				errMessage = "Configuration error: No " \
					"web_console.user_feedback.from_address provided."
				log.error( errMessage )
				raise ConfigurationException, errMessage

			self.authLogin = config.get(
				'web_console.user_feedback.auth_login', '' )
			self.authPassword = config.get(
				'web_console.user_feedback.auth_password', '' )

			# login/password combo is optional but both must be provided
			# together. xor them.
			if bool( self.authLogin ) != bool( self.authPassword ):
				errMessage = "Configuration error: " \
					"web_console.user_feedback.auth_login and " \
					"web_console.user_feedback.auth_password pair must be " \
					"provided together."
				log.error( errMessage )
				raise ConfigurationException, errMessage

			# Attempt a connection to check whether the SMTP service is
			# accessible. This is just for a testing and will record an error
			# message if there is any error during this process.
			if not self._testSMTP():
				log.error( "Failed to connecting or authenticating to SMTP " \
						"service" )
	# _readConfig


	def _testSMTP( self ):
			import smtplib
			smtp = smtplib.SMTP()

			if self._connectSMTP( smtp ):
				smtp.close()
				return True
			else:
				return False
	# _testSMTP


	def _connectSMTP( self, smtp ):
		""" Performs login and authentication on an smtplib.SMTP() object,
		using configured member variables.
		Raise Exception if configuration is missed. Return False if connection
		or authentication to configured SMTP service failed, otherwise return
		True.
		"""

		if not self.isEnabled:
			# This function should never have been called whilst not enabled
			errMessage = "Unable to connect to SMTP server, user feedback " \
				"is not configured."
			log.error( errMessage )
			raise AssertionError, errMessage

		if not self.smtpHost or not self.smtpPort:
			errMessage = "Unable to connect to SMTP server. Host and port " \
				"must be configured."
			log.error( errMessage )
			raise RuntimeError, errMessage

		log.info( "Connecting to SMTP server '%s:%s'", self.smtpHost,
			self.smtpPort )

		try:
			smtp.connect( self.smtpHost, self.smtpPort )
		except Exception, ex:
			log.error( "An error occurred connecting to the SMTP server " \
				"'%s:%s': %s", self.smtpHost, self.smtpPort, str( ex ) )
			return False

		if self.authLogin and self.authPassword:
			try:
				smtp.login( self.authLogin, self.authPassword )
			except Exception, ex:
				log.error( "An error occurred authenticating to the SMTP "
					"server '%s:%s' with login name '%s' : %s",
					self.smtpHost, self.smtpPort, self.authLogin, str( ex ) )
				smtp.close()
				return False

		return True
	# _connectSMTP


	def sendEmail( self, subject, returnAddress, comments, exceptionData,
			versionInfo ):
		if not self.isEnabled:
			# This function should never have been called whilst not enabled
			errMessage = "Unable to send mail, user feedback is not configured."
			log.error( errMessage )
			raise RuntimeError, errMessage
		
		emailBody = comments + ( "\n\n"
			"--------------------------------\n"
			"User/Page Information\n"
			"--------------------------------\n" )
		
		if returnAddress:
			emailBody += "\nReturn Address: %s\n" % returnAddress
		
		emailBody += self.getFeedbackData( versionInfo )["attachedInfo"]
		
		if exceptionData:
			exceptionData = json.loads( exceptionData )
			if exceptionData["exception"]:
				emailBody += "\n\nException: %s" % exceptionData["exception"]
			
			if exceptionData["time"]:
				emailBody += "\nTime: %s" % exceptionData["time"]
				
			if exceptionData["stackTrace"]:
				emailBody += "\n\nStack Trace:\n %s" % \
					exceptionData["stackTrace"]
		
		log.info( "Sending user feedback:\nFrom: %s\nTo: %s\nReply-To: %s\n"
			"Subject: %s\n\n%s", self.fromAddress,
			", ".join( self.toAddressList ), returnAddress, subject, emailBody
			)

		from email.MIMEText import MIMEText

		msg = MIMEText( emailBody )
		msg[ 'Subject' ] = subject
		msg[ 'From' ] = self.fromAddress
		if returnAddress:
			msg[ 'Reply-To' ] = returnAddress
		msg[ 'To' ] = ", ".join( self.toAddressList )

		import smtplib
		smtp = smtplib.SMTP()
		if not self._connectSMTP( smtp ):
			errMessage = "Unable to send mail, configured SMTP servie is not " \
					"accessible."
			log.error( errMessage )
			raise RuntimeError, errMessage

		try:
			try:
				failedAddresses = smtp.sendmail( self.fromAddress,
					self.toAddressList, msg.as_string() )
			except Exception, ex:
				log.error( "An error occurred sending the feedback email: "
					"%s", str( ex ) )
				raise

			if failedAddresses:
				# In practice this point should not be reached because
				# addresses should be validated in advance by the Client
				log.error( "Some of the feedback email addresses were invalid" )
				for address in failedAddresses:
					log.error( "Unable to send feedback to address: %s",
						address )
		finally:
			smtp.close()

		log.info( "User feedback sent." )

		# success (of varying proportions) if this point is reached
		return 1
	# sendEmail


	def getFeedbackData( self, versionInfo ):
		_userIpAddress = cherrypy.request.headers.get( "X-Forwarded-For", "" )
		if not _userIpAddress:
			_userIpAddress = cherrypy.request.headers.get( "Remote-Addr", "" )
		
		returnString = ''
		isEnabled = self.isEnabled
		requestLine = cherrypy.request.requestLine
		referer = cherrypy.request.headers.get( "Referer", "" )
		userAgent = cherrypy.request.headers.get( "User-Agent", "" )
		userName = identity.current.user.user_name
		userGroups = identity.current.user.groups
		firstSection = False
			
		if userName:
			returnString += 'User: %s\n' % userName
			firstSection = True
			
		if userGroups:
			userGroupText = ''
			for index, g in enumerate(userGroups):
				if index > 0:
					userGroupText += ' '
				userGroupText += g.group_name
			if len(userGroupText) > 0:
				returnString += 'Permissions: %s\n' % userGroupText
				firstSection = True
		
		if _userIpAddress:
			returnString += 'IP Address: %s\n' % _userIpAddress
			firstSection = True
			
		if userAgent:
			returnString += 'User Agent: %s\n' % userAgent
		
		if firstSection == True:
			returnString += '\n'
		
		if referer:
			returnString += 'Current Page: %s\n' % referer

		if versionInfo:
			returnString += 'Version:\n{\n'
			returnString += '\n'.join( ['    "%s": "%s",' % (key, value)
				for (key, value) in versionInfo.iteritems()] )
			returnString += '\n}'

		isSmtpServiceOk = False
		if isEnabled:
			isSmtpServiceOk = self._testSMTP()
			
		return dict( 
			isEnabled = isEnabled,
			isSmtpServiceOk = isSmtpServiceOk,
			attachedInfo = returnString
		)
	# getFeedbackData

# class UserFeedback
