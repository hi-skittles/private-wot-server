"This module implements some utility methods."

import BigWorld
import random
import math
import cPickle
import base64
import zlib
from constants import ACCOUNT_ATTR
#import LightGuardPatrolRoutes
#import TeleportPoint

# Currently unused
#def offset(radius):
#	return random.randrange(-radius/2, radius/2)

def offset2(radius):
	angle = random.random()*6.28
	c = math.cos(angle)
	s = math.sin(angle)
	r = random.random()*radius/2.0 + radius/2.0
	return (r*c,r*s)

# TODO: Improve this functions to work with constants.ACCOUNT_ATTR

#def setAccountAttr(attrID, entity):
#	if entity is not None and entity.attrs is not None:
#		account_attrs = entity.attrs
#		account_attrs |= attrID
#		new_attrs = {'rev': 0, 'prevRev': 0, 'account': {'attrs': account_attrs}}
#
#		entity.ownClient.update(cPickle.dumps(new_attrs))

#def removeAccountAttr(attrID, entity):
#	if entity is not None and entity.attrs is not None:
#		account_attrs = entity.attrs
#		account_attrs -= attrID
#		new_attrs = {'rev': 0, 'prevRev': 0, 'account': {'attrs': account_attrs}}
#
#		entity.ownClient.update(cPickle.dumps(new_attrs))

def entitiesOfType(t):
	return [e for e in BigWorld.entities.values() if e.className == t]

# util.py