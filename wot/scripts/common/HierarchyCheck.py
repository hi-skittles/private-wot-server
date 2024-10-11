"""
This is example code demonstrating how to use the Python ResMgr API
to query the entity definitions hierarchy, and compare it to what hierarchy
exists in Python. If they do not match, this module, on importation, will
throw a HierarchyConsistencyError exception.

The module compares entity definition declarations of what  interfaces are
implemented for each entity (i.e. elements within the <Implements> tag). It
then checks that each interface is implemented by a superclass of that entity 
type by checking the entity type's method resolution order.
"""

import ResMgr
import BigWorld

# Set to True if you want an exception raised if errors occur while checking
# the hierarchy. Otherwise, messages will be printed to stdout, and any 
# hierarchical consistencies will not cause the server component to fail 
# on init
RAISE_EXCEPTION_ON_ERROR = False

# ------------------------------------------------------------------------------
# Section: HierarchConsistencyError
# ------------------------------------------------------------------------------

class HierarchyConsistencyError( RuntimeError ):
	pass


# ------------------------------------------------------------------------------
# Section: Module functions
# ------------------------------------------------------------------------------

def getDefInterfaces( entityTypeName ):
	"""
	Retrieve the interface type objects for the named entity type
	@type entityTypeName:	string
	"""
	try:
		entityDef = ResMgr.root['scripts/entity_defs/' + entityTypeName + '.def']
	except:
		raise RuntimeError, \
			"Could not find .def file for entity type %s" % (entityTypeName)

	if not entityDef.has_key( 'Implements' ):
		# this does not implement any interface
		return []

	# retrieve the names of the interfaces implemented by this entity type
	return [
		interfaceElement.asString
		for interfaceElement in entityDef['Implements'].values()
	]


def getEntityTypes():
	"""
	Get a list of entity types as defined in entities.xml.

	@returntype:	list

	"""

	entityTypes = []

	# retrieve the list of names of all entity types known about from resources
	# in scripts/entities.xml

	entityTypeNames = ResMgr.root['scripts/entities.xml'].keys()
	for entityTypeName in entityTypeNames:
		try:
			entityTypeModule = __import__( entityTypeName )
		except ImportError:
			# ignore this - may be a base-only/cell-only entity
			continue


		entityType = getattr( entityTypeModule, entityTypeName )
		entityTypes.append( entityType )

	return entityTypes


def checkEntityType( entityType ):
	"""
	Check the entity def hierarchy for the given entity type.
	It does this by comparing each interface that is implemented by this
	entity type as defined by the entity .def file. For each such interface,
	it loads the interface's type (in the module with the same name) and checks
	that this type is contained within the entity type's method resolution
	order, if it does not, it raises a HierarchyConsistencyError.

	"""
	entityTypeName = entityType.__name__
	entityTypeMRONames = list( x.__name__ for x in entityType.mro() )

	# get declared interfaces from .def file
	interfaceNameList = getDefInterfaces( entityTypeName )

	errorMsgs = []
	# get type objects of the interfaces from script
	for interfaceName in interfaceNameList:

		# check that each interface is in the method resolution order of
		# the entity type
		if not interfaceName in entityTypeMRONames:
			errorMsgs.append(
				"ERROR: %s: %s is required to be derived from interface %s" %
					(entityTypeName, entityTypeName, interfaceName)
			)

	if errorMsgs:
		raise HierarchyConsistencyError, "\n".join( errorMsgs )


def checkTypes():
	"""
	Check all entity types for hierarchical consistency.
	"""
	error = False
	entityTypes = getEntityTypes()
	for entityType in entityTypes:
		try:
			checkEntityType( entityType )
		except HierarchyConsistencyError, e:
			print "%s"  % str(e)
			error = True

	if error:
		errMsg = \
				"Class hierarchy is inconsistent with that defined in " + \
				"entity definitions."
		if RAISE_EXCEPTION_ON_ERROR:
			raise HierarchyConsistencyError, errMsg
		else:
			print "ERROR: " + errMsg

# HierarchyCheck.py
