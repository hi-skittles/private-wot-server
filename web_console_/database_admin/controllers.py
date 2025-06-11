from __builtin__ import help

from turbogears.controllers import expose
from web_console.common import module
from turbogears import identity
import sqlobject
from sqlobject import *

scheme = "mysql://bigworld:bigworld@localhost:3306/player_data_dev1"

class SQLViewer(module.Module):
    def __init__(self, *args, **kw):
        module.Module.__init__(self, *args, **kw)
        self.addPage("Database View", "index")
    
    @identity.require(identity.not_anonymous())
    @expose(template="database_admin.templates.index")
    def index(self, **kw):
        # connection = connectionForURI(scheme)
        # sqlhub.processConnection = connection
        return dict(foo="hello")
