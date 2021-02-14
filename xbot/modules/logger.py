import os
import time, datetime

from . import botdb

def log(bot, channel, nick, message):
	date = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
	file = open('/var/log/xbot/%s.txt' % channel, 'a+')
	if message.startswith("\x01ACTION"):
		file.write("%s * %s %s\r\n" % (date, nick, message[8:-1]))
		action = 1
	else:
		for line in message.split("\n"):
			if line:
				file.write("%s <%s> %s\r\n" % (date, nick, line))
		action = 0

	file.close()

	db = botdb.BotDB(bot).connect()

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
