from bwdebug import DEBUG_MSG

BILLING_SYSTEM = "mysql"

if BILLING_SYSTEM == "mysql":
	from mysql_billing import BillingSystem as connectToBillingSystem
else:
	def connectToBillingSystem():
		return None


def onInit(isReload):
	DEBUG_MSG('Billing System (%s): %s' % (isReload, BILLING_SYSTEM))

# db/wot.py
