import BigWorld

import util
from bwdecorators import watcher


# Get the number of online accounts
# -----------------------------------------------------------------------------
@watcher("onlineAccounts")
def onlineAccounts():
	return len(util.entitiesOfType("Account"))
