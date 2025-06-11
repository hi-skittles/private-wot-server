from sqlobject import *
from turbogears.database import PackageHub

hub = PackageHub("cluster_control")
__connection__ = hub
