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
		self.addPage("Overview", "index")
		self.addPage("View", "view")
		self.addPage("Modify", "modify")
	
	def _fetch_total_players(self):
		"""Return the total number of players in the database."""
		db = MySQLdb.connect(user="bigworld", passwd="bigworld", db="player_data_dev1")
		cursor = db.cursor()
		query = """
                select logOnName
                from accounts1
                limit 10; \
		        """
		cursor.execute(query)
		rows = cursor.fetchall()
		cursor.close()
		db.close()
		return list(rows), len(rows)
	
	@identity.require(identity.not_anonymous())
	@expose(template="database_admin.templates.index")
	def index(self):
		# connection = connectionForURI(scheme)
		# sqlhub.processConnection = connection
		from web_console.common import util
		username = util.getSessionUsername()
		del util
		players, total = self._fetch_total_players()
		return dict(username=username, players=players, total=total)
	
	def _fetch_player_data(self, table, email):
		"""Return a dictionary of player stats for the given email or None."""
		db = MySQLdb.connect(user="bigworld", passwd="bigworld", db="player_data_dev1")
		cursor = db.cursor()
		query = "SELECT * FROM {0} WHERE email=%s".format(table)
		cursor.execute(query, (email,))
		row = cursor.fetchone()
		db.commit()
		if not row:
			return None
		
		import cPickle, base64
		# columns = ["account", "cache", "economics", "offers", "stats", "intUserSettings", "eventsData"]
		cursor.execute("SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = %s;", (table,))
		columns = [col[0] for col in cursor.fetchall()]
		cursor.close()
		db.commit()
		db.close()
		data = {}
		for i, col in enumerate(columns):
			val = row[i]
			if val is None:
				continue
			try:
				data[col] = cPickle.loads(base64.b64decode(val))
			except Exception as e:
				data[col] = val
		return data
	
	@identity.require(identity.not_anonymous())
	@expose(template="database_admin.templates.view_player")
	def view(self, email=None):
		data = None
		if email:
			try:
				data = self._fetch_player_data('accounts1', email)
			except Exception, e:
				data = {"error": str(e)}
		return dict(email=email, data=data)
		
	@identity.require(identity.not_anonymous())
	@expose(template="database_admin.templates.modify_player")
	def modify(self, email=None, table=None):
		data = None
		if email:
			try:
				data = self._fetch_player_data(table, email)
			except Exception, e:
				data = {"error": str(e)}
		return dict(email=email, data=data, first_ten=self._fetch_total_players()[0])
