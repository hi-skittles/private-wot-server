import json

class Encoder( json.JSONEncoder ):
	def default( self, obj ):
		if type( obj ).__name__ in \
				("PyArrayDataInstance", "Vector2", "Vector3", "Vector4"):
			return list( obj )

		return json.JSONEncoder.default( self, obj )

def asJSON( obj ):
	return json.dumps( obj, cls = Encoder )

# json_convert.py
