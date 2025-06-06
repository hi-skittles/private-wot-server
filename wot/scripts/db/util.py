import BigWorld


def entitiesOfType(t):
	return [e for e in BigWorld.entities.values() if e.className == t]
