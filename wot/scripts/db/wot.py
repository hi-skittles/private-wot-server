from bwdebug import DEBUG_MSG

BILLING_SYSTEM = ""

if BILLING_SYSTEM == "sqlite":
	from sqlite_billing_dev import BillingSystem as connectToBillingSystem
else:
	def connectToBillingSystem():
		return None

def onInit(isReload):
	DEBUG_MSG('Billing System (%s): %s' % (isReload, BILLING_SYSTEM))

# db/wot.py
