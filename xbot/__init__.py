import signal
import socket
import ssl

from . import irc

class Initialise(object):
	def __init__(self, hosts, config):
		self.hosts = hosts
		self.bot = irc.Client(config)
		signal.signal(signal.SIGINT, self.bot.disconnect)
		signal.signal(signal.SIGTERM, self.bot.disconnect)

	def run(self):
		i = 0
		while True:
			if i == len(self.hosts): i = 0
			try:
				self.bot.connect(self.hosts[i][0], int(self.hosts[i][1]))
			except (irc.ServerDisconnectedException, socket.error):
				pass
