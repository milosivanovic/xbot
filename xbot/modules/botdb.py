import MySQLdb

class BotDB(object):

	def __init__(self, bot):
		self.host = bot.config.get('module: botdb', 'db_host')
		self.user = bot.config.get('module: botdb', 'db_user')
		self.pw = bot.config.get('module: botdb', 'db_pass')
		self.db = bot.config.get('module: botdb', 'db_name')
	
	def connect(self):
		if self.host and self.user and self.pw and self.db:
			return MySQLdb.connect(host=self.host, user=self.user, passwd=self.pw, db=self.db)