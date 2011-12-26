#!/usr/bin/python

import irc
import signal
import ConfigParser

class Initialise(object):
	def __init__(self, servers, port):
		self.servers = servers
		self.port = port
		self.config = ConfigParser.ConfigParser()
		self.config.read('/etc/xbot/xbot.conf')
		
		self.bot = irc.Client(self.config)
		signal.signal(signal.SIGINT, self.bot.disconnect)
		signal.signal(signal.SIGTERM, self.bot.disconnect)
	
	def run(self):
		i = 0
		while True:
			if i == len(self.servers): i = 0
			try:
				self.bot.connect(self.servers[i], self.port)
			except IOError:
				i += 1
