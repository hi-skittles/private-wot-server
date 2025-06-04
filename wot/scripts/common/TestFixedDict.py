class TestFixedDictType:
	"""
	Class of objects that correspond to the TEST_FIXED_DICT alias.
	Note that this is not a dict at all, it uses class customised FIXED_DICT
	to implement persistence on BigWorld DbApp.
	"""
	def __init__( self, a, b, c ):
		self.a = a
		self.b = b
		self.c = c


class TestFixedDictWrapper:
	def createObjFromDict( self, dict ):
		return TestFixedDictType( dict['a'], dict['b'], dict['c'] )

	def getDictFromObj( self, obj ):
		return dict( a = obj.a, b = obj.b, c = obj.c )

	def isSameType( self, obj ):
		return isinstance( obj, TestFixedDictType )

instance = TestFixedDictWrapper()
