import MySQLdb

from turbogears.controllers import expose
from web_console.common import module
from turbogears import identity
import sqlobject
from sqlobject import *

scheme = "mysql://bigworld:bigworld@localhost:3306/player_data_dev1"

class DBAIndex(module.Module):
    def __init__(self, *args, **kw):
        module.Module.__init__(self, *args, **kw)
        self.addPage("Database Overview", "index")
        self.addPage("Database View", "view")
        self.addPage("Database Modify", "modify")
    
    @identity.require(identity.not_anonymous())
    @expose(template="database_admin.templates.index")
    def index(self):
        # connection = connectionForURI(scheme)
        # sqlhub.processConnection = connection
        return dict(foo="hello")
