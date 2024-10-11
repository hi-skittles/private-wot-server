import logging
from collections import OrderedDict
import traceback

import BigWorld
import ResMgr


log = logging.getLogger( __name__ )

# Set of classes that have had standard watchers added
standardWatchersAdded = set()

def addStandardWatchers( service ):
	"""
	This method adds the standard watchers for the given service.

	@param service 	The service name, or the service class itself.
	"""
	if type( service ) is type and issubclass( service, BigWorld.Service ):	
		serviceName = service.__name__
	else:
		serviceName = service
	

	def getIsRunning():
		try:
			BigWorld.localServices[ serviceName ]
			return True
		except:
		   return False

	def setIsRunning( value ):
		try:
			if value.lower() in ("true", "1"):
				BigWorld.startService( serviceName )
			else:
				BigWorld.stopService( serviceName )
		except:
	   		pass

	# prevent watchers from being added more than once.
	# eg: stopping and (re-)starting a service
	if serviceName not in standardWatchersAdded:
		BigWorld.addWatcher( "servicesStaticConfig/" + serviceName + 
			"/isRunning",
			getIsRunning, setIsRunning )

		standardWatchersAdded.add( serviceName )

# addStandardWatchers


class InvalidServiceConfiguration( ValueError ):
	""" Indicates a synactic or semantic service configuration error """
	pass
# end class InvalidServiceConfiguration


class ServiceConfigMeta( type ):
	"""
	Metaclass for service config classes so that configuration options are
	exposed as watcher values and can also be read from a file at load-time and
	after.

	For a class that uses this metaclass (or derives from ServiceConfig), an
	'options' attribute is added that contain all the options detected in the
	class's dictionary. Those attributes in the dictionary that don't start
	with an underscore are assumed to be a configuration option.

	Options are typically named using a combination of uppercase letters and
	underscores to separate words. The equivalent watcher paths for each option
	is named using camel case, though this can be overridden to use a different
	name.

	"""
	def __init__( klass, name, bases, dct ):
		"""
		Override from type.
		"""
		type.__init__( klass, name, bases, dct )
		if bases == (object,):
			return

		options = ServiceConfigOptions( klass )
		setattr( klass, "options", options )

		fileConfigs = []

		readOnlyOptions = set( klass._getReadOnlyOptions( klass ) )

		for name, value in dct.items():
			if name.startswith( '_' ) or name == 'Meta':
				continue

			if isinstance( value, ServiceConfigOption ):
				option = value
				setattr( klass, name, option.value )
			elif type( value ) == bool:
				option = ServiceConfigBoolOption( value )
			else:
				option = ServiceConfigOption( value, converter = type( value ) )

			option.name = name
			option.configClass = klass
			options.addOption( option )

			if isinstance( option, ServiceConfigFileOption ):
				fileConfigs.append( option )

			if name in readOnlyOptions:
				option.isReadOnly = True

		for fileConfig in fileConfigs:
			fileConfig.readConfigFromPath( shouldBlock = True )

		serviceName = klass._getServiceName( klass )
		if serviceName:
			watcherPath = 'servicesStaticConfig/' + serviceName
			addStandardWatchers( serviceName )
			klass.addWatchers( watcherPath )


	@staticmethod
	def _getServiceName( klass ):
		try:
			return klass.Meta.SERVICE_NAME	
		except AttributeError:
			return None


	@staticmethod
	def _getReadOnlyOptions( klass ):
		try:
			return klass.Meta.READ_ONLY_OPTIONS
		except AttributeError:
			return []


class ServiceConfigOption( object ):
	"""
	This class represents each configuration option.
	"""
	def __init__( self, initialValue, converter = None, optionName = None,
			isReadOnly = False, getter = None ):
		"""
		Constructor.

		Initially options are not bound to a config class, which means that
		they are nameless and they have a floating value. Options will be bound
		as part of the class initialisation from the metaclass, which sets both
		the name and the configClass property on the option object.

		@param initialValue 	The initial value of the option.
		@param converter 		If set, this is used to convert the option's
								value from a string when being set from a
								watcher.
		@param optionName 		The option name. If none, one will be generated
								by converting the uppercase/underscore name to
								a camel-case name.
		@param isReadOnly 		Whether watchers for this option should be
								read-only.
		@param getter			The getter function to use. If None, a getter
								function that simply returns the value is used.
		"""
		self._name = None # This is set from the metaclass
		self._configClass = None # This is set from the metaclass
		self._value = initialValue
		self._converter = converter
		self._optionName = optionName
		self._isReadOnly = isReadOnly
		self._customGetter = getter


	def readConfig( self, dataSection ):
		"""
		This method reads the option from the given data section.
		"""
		if self._optionName in dataSection.keys():
			self.value = dataSection.readString( self._optionName )


	def addWatcherToPath( self, parentPath ):
		"""
		This method exposes this option as a watcher under the given path.

		@param parentPath 	The watcher path under which to add a watcher for
							this option.
		"""
		path = parentPath + "/" + self._optionName

		try:
			BigWorld.delWatcher( path )
		except:
			pass

		if self.isReadOnly:
			BigWorld.addWatcher( path, self.getter )
		else:
			BigWorld.addWatcher( path, self.getter, self.setter )


	@staticmethod
	def convertUppercaseToCamelCase( s ):
		"""
		This method is used to convert a presumed-to-be uppercase/underscore
		name to camel-case.
		"""
		out = ""
		for i, component in enumerate( s.split( "_" ) ):
			if i:
				component = component[0].upper() + component[1:].lower()
			else:
				component = component.lower()

			out += component
		return out


	@property
	def name( self ):
		"""
		This property returns the name.
		"""
		return self._name


	@name.setter
	def name( self, name ):
		"""
		This method sets the name.
		"""
		self._name = name
		if self._optionName is None:
			self._optionName = \
				ServiceConfigOption.convertUppercaseToCamelCase( name )


	@property
	def value( self ):
		"""
		This method returns the current value of the option.
		"""
		if self._configClass:
			return getattr( self._configClass, self._name )
		else:
			return self._value


	@value.setter
	def value( self, newValue ):
		"""
		This method sets the value from the given string.
		"""
		if self._converter:
			newValue = self._converter( newValue )

		if self._configClass:
			setattr( self._configClass, self._name, newValue )
		else:
			self._value = newValue


	@property
	def getter( self ):
		"""
		This method returns a getter function for this option.
		"""
		if self._customGetter:
			return self._customGetter
		return lambda: str( self.value )


	@property
	def setter( self ):
		"""
		This method returns a setter function for this option.
		"""
		def setterFunction( v ):
			self.value = v
		return setterFunction


	@property
	def configClass( self ):
		"""
		This method returns this option's configuration class.
		"""
		return self._configClass


	@configClass.setter
	def configClass( self, klass ):
		"""
		This method sets the configuration class for this option, binding the
		option to this class.
		"""
		if self._configClass is not None:
			raise ValueError( "Already bound" )
		elif klass is None:
			raise TypeError( "Must bind to a configuration class" )

		self._configClass = klass
		if klass and self._value:
			setattr( klass, self._name, self._value )
			del self._value


	@property
	def isReadOnly( self ):
		"""
		This method returns whether this option's watcher is read-only.
		"""
		return self._isReadOnly


	@isReadOnly.setter
	def isReadOnly( self, value ):
		"""
		This method sets whether this option's watcher is read-only.
		"""
		self._isReadOnly = bool( value )


	@property
	def optionName( self ):
		"""
		This method returns the name used by watchers and configuration files
		when referring to this object.
		"""
		return self._optionName


	def __repr__( self ):
		"""
		This method returns the string representation of this object.
		"""
		return "Option {}: {}".format( self._name, self.getter() )


class ServiceConfigPortsOption( ServiceConfigOption ):
	"""
	This class can be used for an option that parses a list of ports. The
	configuration option, when parsing a data section expects a section with
	children named port. This option does not support setting at run-time.
	"""

	def __init__( self, initialValue, optionName = None ):
		"""
		Constructor.
		"""
		ServiceConfigOption.__init__( self, initialValue,
			optionName = optionName )
		self.isReadOnly = True


	def readConfig( self, dataSection ):
		"""
		Override from ServiceConfigOption.
		"""
		self.value = list( dataSection.readInts( self.optionName + "/port" ) )


class ServiceConfigFileOption( ServiceConfigOption ):
	"""
	This option can be used to specify a XML configuration file for the entire
	configuration class.

	When the class is first loaded, the configuration is called in blocking
	mode. If this value is set to a new path, then that configuration is loaded
	from a file asynchronously.
	"""
	def __init__( self, initialValue, optionName = None ):
		"""
		Constructor.
		"""
		ServiceConfigOption.__init__( self, initialValue,
			converter = self._convert,
			optionName = optionName )


	def _readConfigAsync( self, path ):
		"""
		This method opens a data section asynchronously and reads the option
		values from the file for the entire configuration class that this
		option is bound to.

		@param path 	The path to the configuration data section.
		"""
		def callback( section ):
			if not section:
				return
			self._configClass.readConfig( section )
			self._value = path

		BigWorld.fetchDataSection( path, callback )


	def _convert( self, path ):
		"""
		This method is called when a watcher value for the configuration is set
		to a new path. New configuration is loaded from that file
		asynchronously, and set on this option's bound configuration class.
		"""
		self.readConfigFromPath( path )
		return path


	def readConfig( self, section ):
		"""
		Override from ServiceConfigOption. We don't read our own option value
		from our own configuration path!
		"""
		return


	def readConfigFromPath( self, path = None, shouldBlock = False ):
		"""
		This method reads a configuration path from file.

		@param path			The path to read from, or if None, the path is
							taken to be this option's current value.
		@param shouldBlock 	Whether the data section referred to by the path
							should be opened synchronously if True, or
							asynchronously if False.
		"""
		if path is None:
			path = self.value

		if shouldBlock:
			self._value = path
			self._configClass.readConfig( ResMgr.openSection( path ) )
		else:
			self._readConfigAsync( path )


class ServiceConfigBoolOption( ServiceConfigOption ):
	"""
	This option can be used for Boolean values. When the option's watcher value
	is set, the value is taken from one of two text strings, "true" or "false".
	"""
	def __init__( self, initialValue, optionName = None ):
		"""
		Constructor.

		@param initialValue 	The initial value.
		@param optionName 		The option name to use, or None to generate.
		"""
		ServiceConfigOption.__init__( self, bool( initialValue ),
			converter = self._convert,
			optionName = optionName )

	def _convert( self, value ):
		"""
		This method converts the given text string value to an appropriate
		True/False value.
		"""
		if value.lower() == "true":
			return True
		elif value.lower() == "false":
			return False
		raise ValueError( "Cannot convert boolean value, must be "
			"\"true\" / \"false\"" )


class ServiceConfigOptions( object ):
	"""
	Instances of this class are used to hold a collection of
	ServiceConfigOption objects for a configuration class.

	Attribute access on this object will look up configuration options by name.
	"""
	def __init__( self, configClass ):
		"""
		Constructor.

		@param configClass 	The configuration class.
		"""
		self._configClass = configClass
		self._options = OrderedDict()


	def addOption( self, option ):
		"""
		This method adds the given option to the collection.
		"""
		self._options[option.name] = option


	def __iter__( self ):
		"""
		This method returns an iterator through the collection of options.
		"""
		return iter( self._options.values() )


	def __getattr__( self, name ):
		"""
		This method returns the configuration option for the given name.
		"""
		if name.startswith( '_' ):
			return object.__getattr__( name )
		return self._options[name]


class ServiceConfig( object ):
	"""
	Configuration super-class.
	"""
	__metaclass__ = ServiceConfigMeta

	@classmethod
	def addWatchers( klass, path ):
		"""
		This method adds watchers for the options under this class for the
		given parent path.

		@param path 	Watchers for options will be added under this watcher
						path.
		"""
		for option in klass.options:
			option.addWatcherToPath( path )


	@classmethod
	def readConfig( klass, dataSection ):
		"""
		This method reads configuration option values from the given data
		section.

		@param dataSection 	The data section to read configuration option
							values from.
		"""
		for option in klass.options:
			try:
				option.readConfig( dataSection )
			except Exception as e:
				log.error( "Could not read config for %s.%s: %s",
					klass.__name__, option.name, e )


# service_utils.py
