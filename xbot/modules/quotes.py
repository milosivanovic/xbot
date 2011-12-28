import datetime
import MySQLdb
import re

def get_quote(bot, args):

	db = MySQLdb.connect(host=bot.config.get('general', 'db_host'), user=bot.config.get('general', 'db_user'), passwd=bot.config.get('general', 'db_pass'), db=bot.config.get('general', 'db_name'))
	cursor = db.cursor()

	def sql(query, vars):
		try:
			return cursor.execute(query, vars)
		except MySQLdb.OperationalError as e:
			bot._sendq(("PRIVMSG", bot.remote['sendee']), "!quotes: %s" % re.match("Got error '(.+)' from regexp", e[1]).group(1))
			return None
	
	def gen_kw(keywords):
		result = ""
		for keyword in keywords:
			result += (" AND message LIKE '%%%s%%'" % re.escape(keyword)).replace("%", "%%")
		return result
		
	if len(args) > 1:
	
		channel = bot.remote['receiver']
		nick = bot.remote['nick']
		
		if args[1].lower() != bot.nick.lower():
			if len(args) == 2:
				if args[1] != "*":
					numrows = sql("SELECT * FROM quotes WHERE channel = %s AND nick REGEXP %s ORDER BY rand() LIMIT 1", (channel, args[1]))
					if numrows:
						return output_quote(bot, cursor, nick)
					elif numrows is not None:
						return "No quotes from %s found." % args[1]
				else:
					numrows = sql("SELECT * FROM quotes WHERE channel = %s AND nick != '" + re.escape(bot.nick) + "' ORDER BY rand() LIMIT 1", (channel,))
					if numrows:
						return output_quote(bot, cursor, nick)
					elif numrows is not None:
						return "No quotes in database yet."
						
			elif len(args) >= 3:
				search = ' '.join(args[2:])
				if args[1] != "*":
					if search.startswith("/") and search.endswith("/"):
						type = "regexp"
						numrows = sql("SELECT * FROM quotes WHERE channel = %s AND nick REGEXP %s AND message REGEXP %s", (channel, args[1], search[1:-1]))
					else:
						type = "keywords"
						numrows = sql("SELECT * FROM quotes WHERE channel = %s AND nick REGEXP %s" + gen_kw(search.split()), (channel, args[1]))
				else:
					if search.startswith("/") and search.endswith("/"):
						type = "regexp"
						numrows = sql("SELECT * FROM quotes WHERE channel = %s AND nick != '" + re.escape(bot.nick) + "' AND message REGEXP %s", (channel, search[1:-1]))
					else:
						type = "keywords"
						numrows = sql("SELECT * FROM quotes WHERE channel = %s AND nick != '" + re.escape(bot.nick) + "'" + gen_kw(search.split()), (channel,))
						
				if numrows > 0 and numrows <= 15:
					if numrows > 1:
						bot._sendq(("PRIVMSG", channel), '%s result%s sent.' % (numrows, '' if numrows == 1 else 's'))
					return output_quote(bot, cursor)
				elif numrows > 15:
					if type == "keywords":
						return "%d quotes found." % numrows
					elif type == "regexp":
						return "%d quotes matched." % numrows
				else:
					if type == "keywords":
						return "No quotes with keywords |%s| found." % search
					elif type == "regexp":
						return "No quotes with regexp %s matched." % search
		else:
			return "Nah. My own quotes are too contaminated."
	else:
		return "Usage: !%s <nick|*> [<keywords|/regexp/>]" % args[0]

def output_quote(bot, cursor):
	import scanner
	
	for row in cursor.fetchall():
		if not row[4]:
			prepend = "%s | <%s> %s"
		else:
			prepend = "%s | * %s %s"
		
		output = prepend % (str(datetime.datetime.fromtimestamp(int(row[1]))), row[3], row[5])
		result = scanner.scan(bot, output) or ''
		
		if cursor.rowcount > 1:
			bot._sendq(("NOTICE", bot.remote['nick']), '\n'.join([output, result]))
		else:
			return '\n'.join([output, result])