import os
import time, datetime
import MySQLdb

def log(bot, channel, nick, message):
	date = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
	file = open('/var/log/xbot/%s.txt' % channel, 'a+')
	if message.startswith("\x01ACTION"):
		file.write("%s * %s %s\r\n" % (date, nick, message[8:-1]))
		action = 1
	else:
		for line in message.split("\n"):
			file.write("%s <%s> %s\r\n" % (date, nick, line))
		action = 0
		
	file.close()
	
	try:
		db = MySQLdb.connect(host=bot.config.get('general', 'db_host'), user=bot.config.get('general', 'db_user'), passwd=bot.config.get('general', 'db_pass'), db=bot.config.get('general', 'db_name'))
	except MySQLdb.OperationalError:
		return
	
	cursor = db.cursor()
	if not message.startswith("!quote"):
		if action: message = message[8:-1]
		cursor.execute("""
							INSERT INTO `quotes`
								(time, channel, nick, action, message)
							VALUES
								(%s, %s, %s, %s, %s)
		""", [int(time.time()), channel, nick, action, message])
		db.commit()