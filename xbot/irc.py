import sys, os
import socket
import ssl
import select
import time
import datetime
import traceback
import importlib

from . import modules

class ServerDisconnectedException(Exception):
	pass


class Client(object):

	def __init__(self, config):
		self.config = config
		self.sendq = []
		self.recvq = []
		self.termop = "\r\n"
		self.verbose = True
		self.delay = False
		self.closing = False
		self.connected = False
		self.timeout = 300
		self.version = 3.0
		self.env = sys.platform
		self.inputs = []
		self.outputs = []

		socket.setdefaulttimeout(self.timeout)

		self.mgmt_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.mgmt_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.mgmt_server.setblocking(0)

		self.mgmt_server.bind(('', 10000))
		self.mgmt_server.listen(0)
		self._log("dbg", "Listening on management port (%s)..." % str(self.mgmt_server.getsockname()))
		self.inputs.append(self.mgmt_server)

	def connect(self, server, port):
		self.connected = False

		self.irc_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.irc_server = ssl.wrap_socket(self.irc_server)

		self._log("dbg", "Connecting to Freenode (%s:%s)..." % (server, port))
		self.irc_server.connect((server, port))
		self._log("dbg", "Connected.")
		self.irc_server.setblocking(0)
		self.connected = True

		self.inputs.append(self.irc_server)

		self._log("dbg", "Starting main loop...")
		self._loop()

	def _loop(self):
		p = Parser(self, self.config)
		while True:
			self._select()

			if self.closing:
				break

			if len(self.sendq) > 0:
				self._send(self.irc_server)

			if self.recvq:
				lines = ''.join(self.recvq).split(self.termop)
				del self.recvq[:]
				if lines[-1]:
					self.recvq.append(lines[-1])
					del lines[-1]
				n = 1
				for n, line in enumerate(lines, 1):
					if line:
						self._log('dbg', 'Parsing %s' % repr(line))
						p.interpret(line)
					else:
						n -= 1
				if n > 1:
					self._log('dbg', 'Parsed %d sentence%s.%s' % (n, '' if n == 1 else 's', ' More pending.' if self.recvq else ''))

			if len(self.sendq) > 0:
				self.outputs.append(self.irc_server)

	def _select(self):
		self._log("dbg", "Waiting for select()...")
		ready_read, ready_write, _ = select.select(self.inputs, self.outputs, [], self.timeout)
		self._log("dbg", "select() returned %d read, %d write" % (len(ready_read), len(ready_write)))

		for sock in ready_read:
			if sock is self.mgmt_server:
				conn, addr = self.mgmt_server.accept()
				conn.setblocking(0)
				self._log("dbg", "New management connection from %s:%d" % (addr[0], addr[1]))
			else:
				self._recv(sock, 1500)

		for sock in ready_write:
			self.outputs.remove(sock)

		if not ready_read and not ready_write:
			self._log("dbg", "select() timed out")
			self._shutdown()

	def _shutdown(self):
		self._log("dbg", "Shutting down IRC socket...")
		self.irc_server.shutdown(socket.SHUT_RDWR)
		#self.irc_server = self.irc_server.unwrap()
		#self.irc_server.shutdown(socket.SHUT_RDWR)
		self.irc_server.close()
		#self.closing = True
		self.inputs.remove(self.irc_server)
		try:
			self.outputs.remove(self.irc_server)
		except ValueError:
			pass
		self.connected = False
		raise ServerDisconnectedException

	def disconnect(self, n, frame):
		if self.connected:
			self._sendq(['QUIT'], "See ya~")
			self._send(self.irc_server)
		self.connected = False
		sys.exit()

	def _recv(self, sock, bytes):
		try:
			data = sock.recv(bytes).decode('utf8')
		except ssl.SSLError as e:
			if e.errno == ssl.SSL_ERROR_WANT_READ:
				self._log("dbg", "Couldn't read: SSL_ERROR_WANT_READ, re-running select()")
				self._log("dbg", "recvq contains %s" % self.recvq)
				return
		if data:
			if self.verbose:
				self._log('in', data)
				self.recvq.append(data)
		else:
			if sock in self.inputs:
				addr = sock.getpeername()
				self._log("dbg", "Closed connection from %s:%d" % (addr[0], addr[1]))
				if sock == self.irc_server:
					self._shutdown()
			else:
				raise RuntimeError("Socket connected to %s not found in socket list %s" % (sock.getpeername(), self.inputs))

	def _sendq(self, left, right = None):
		if right:
			limit = 445
			for line in right.splitlines(): # don't use self.termop as \r and \n are both treated as newlines in the IRC protocol, otherwise this is exploitable
				if line:
					lines = [line[i:i+limit] for i in range(0, len(line), limit)]
					for n in range(len(lines)):
						self.sendq.append("%s :%s%s" % (' '.join(left), lines[n], self.termop))
		else:
			self.sendq.append("%s%s" % (' '.join(left), self.termop))

	def _send(self, sock):
		lines = len(self.sendq)
		burst = 5
		delay = 2
		for i in range(0, lines, delay):
			if not self.delay:
				buffer = ''.join(self.sendq[:burst])
				del self.sendq[:burst]
				self.delay = True
			else:
				buffer = ''.join(self.sendq[:delay])
				del self.sendq[:delay]
				time.sleep(delay)
			if self.verbose:
				self._log('out', buffer)
			sock.write(buffer.encode('utf8'))
			break

		if len(self.sendq) > 0:
			self._log('dbg', 'There are still %d bytes queued to be sent.' % sum(len(q) for q in self.sendq))
		else:
			self.delay = False

	def _log(self, flow, buffer):
		log = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
		buffer = buffer.replace(self.config.get(self.config.active_network, 'password'), '***********')
		if flow == "out":
			_pad = "<<<"
			self._log('dbg', 'Sending %d bytes' % len(buffer))
		elif flow == "in":
			_pad = ">>>"
			self._log('dbg', 'Received %d bytes' % len(buffer))
		elif flow == "dbg":
			_pad = "DBG"
			buffer += self.termop
		for index, line in enumerate(buffer.split(self.termop)):
			if line:
				if index == 0:
					pad = _pad
				else:
					pad = "   "

				output = "%s %s %s" % (log, pad, line)
				print(output)
				for conn in self.inputs:
					if conn != self.irc_server:
						try:
							conn.send((output + self.termop).encode('utf8'))
						except IOError:
							pass


class Parser(object):
	def __init__(self, bot, config):
		self.bot = bot
		self.config = config
		#super(Parser, self).__init__(config)
		self.network = config.active_network
		self.init = {
			'ident': 0, 'retries': 0, 'ready': False, 'log': True,
			'registered': True if config.has_option(self.network, 'password') else False,
			'identified': False, 'joined': False
		}
		self.inv = {
			'rooms': {},
			'banned': []
		}
		self.remote = {}
		self.previous = {}
		self.voice = True
		self.name = config.get(self.network, 'nick')
		self.admin = config.get(self.network, 'admin')

	def interpret(self, line):
		self.remote['server'] = None
		self.remote['nick'] = None
		self.remote['user'] = None
		self.remote['host'] = None
		self.remote['receiver'] = None
		self.remote['misc'] = None
		self.remote['message'] = None

		try:
			if line.startswith(':'):
				if ' :' in line:
					args, trailing = line[1:].split(' :', 1)
					args = args.split()
				else:
					args = line[1:].split()
					trailing = args[-1]

				if "@" in args[0]:
					client = args[0].split("@")
					self.remote['nick'] = client[0].split("!")[0]
					self.remote['user'] = client[0].split("!")[1]
					self.remote['host'] = client[1]
				else:
					self.remote['server'] = args[0]

				self.remote['mid'] = args[1]
				self.remote['message'] = trailing

				try:
					self.remote['receiver'] = args[2]
				except IndexError:
					pass
				try:
					self.remote['misc'] = args[3:]
				except IndexError:
					pass
				self._init()

				if self.init['ident'] and self.remote['mid'] in ['376', '422']:
					self.init['ready'] = True

				if self.init['ready']:
					if self.remote['message']:
						self.remote['sendee'] = self.remote['receiver'] if self.remote['receiver'] != self.nick else self.remote['nick']
						try:
							if self.init['log'] and self.init['joined'] and self.remote['mid'] == "PRIVMSG":
								modules.logger.log(self, self.remote['sendee'], self.remote['nick'], self.remote['message'])
							modules.io.read(self)
						except:
							error_message = "Traceback (most recent call last):\n" + '\n'.join(traceback.format_exc().split("\n")[-4:-1])
							self.bot._sendq(("NOTICE", self.remote['sendee'] or self.admin), error_message)
					if self.init['joined']:
						self._updateNicks()
			else:
				arg	= line.split(" :")[0]
				message = line.split(" :", 1)[1]
				self._init()

				if arg == "PING":
					self.bot._sendq(['PONG'], message)
		except Exception as e:
			self.bot._log("dbg", "Error parsing input: %s (%s)" % (repr(line), e))

	def _sendq(self, left, right = None):
		if self.init['log'] and self.init['joined'] and left[0] == "PRIVMSG":
			if self.remote['receiver'] == self.nick: self.remote['receiver'] = self.remote['nick']
			if type(right) != str: raise AssertionError("send queue must be <type 'str'> but was found as %s" % type(right))
			modules.logger.log(self, left[1], self.nick, right)
		self.bot._sendq(left, right)

	def _init(self):
		if self.remote['message'] and self.init['ident'] is not True:
			if self.remote['message']:
				self.init['ident'] += 1
		if self.init['ident'] > 1:
			while not self.init['retries'] or self.remote['mid'] in ['433', '437']:
				if self.remote['mid'] == '433':
					self._log("dbg", "Nick already in use, waiting 30s...")
					time.sleep(30)
				self._ident()
				break
			if self.remote['mid'] == "001":
				self.init['ident'] = True

	def _ident(self):
		self.nick = self.name # + "_" * self.init['retries']
		self.bot._sendq(("NICK", self.nick))
		self.bot._sendq(("USER", self.nick, self.nick, self.nick), self.nick)
		self.init['retries'] += 1

	def _login(self):
		self.bot._sendq(("PRIVMSG", "NickServ"), "IDENTIFY %s" % self.config.get(self.network, 'password'))

	def _updateNicks(self):
		if self.remote['mid'] == "JOIN":
			if self.remote['nick'] == self.nick:
				self.inv['rooms'][self.remote['message']] = {}
			else:
				self.inv['rooms'][self.remote['message']][self.remote['nick']] = {}
		elif self.remote['mid'] == "353":
			for user in self.remote['message'].split():
				self.inv['rooms'][self.remote['misc'][1]][user.lstrip("~.@%+")] = {}
				if __import__('re').search('^[~\.@%\+]', user):
					if user[0] in ['~', '.']:
						mode = 'q'
					elif user[0] == '@':
						mode = 'o'
					elif user[0] == '%':
						mode = 'h'
					elif user[0] == '+':
						mode = 'v'
					self.inv['rooms'][self.remote['misc'][1]][user[1:]]['mode'] = mode or None
				else:
					self.inv['rooms'][self.remote['misc'][1]][user]['mode'] = None
		elif self.remote['mid'] == "PART":
				if self.remote['nick'] == self.nick:
					del self.inv['rooms'][self.remote['receiver']]
				else:
					del self.inv['rooms'][self.remote['receiver']][self.remote['nick']]
		elif self.remote['mid'] == "KICK":
			if self.remote['misc'][0].lower() != self.nick.lower():
				del self.inv['rooms'][self.remote['receiver']][self.remote['misc'][0]]
			else:
				del self.inv['rooms'][self.remote['receiver']]
		elif self.remote['mid'] == "NICK":
			for room in self.inv['rooms']:
				if self.remote['nick'] in self.inv['rooms'][room]:
					self.inv['rooms'][room][self.remote['message']] = self.inv['rooms'][room][self.remote['nick']]
					del self.inv['rooms'][room][self.remote['nick']]
			if self.remote['nick'].lower() in self.inv['banned']:
				self.inv['banned'][self.inv['banned'].index(self.remote['nick'].lower())] = self.remote['message'].lower()
		elif self.remote['mid'] == "QUIT":
			for room in self.inv['rooms']:
				if self.remote['nick'] in self.inv['rooms'][room]:
					del self.inv['rooms'][room][self.remote['nick']]
		elif self.remote['mid'] == "MODE":
			if len(self.remote['misc']) == 2:
				if self.remote['misc'][0].startswith("+") and self.remote['misc'][0][1] in ['o', 'h', 'v']:
					self.inv['rooms'][self.remote['receiver']][self.remote['misc'][1]]['mode'] = self.remote['misc'][0][1]
				elif self.remote['misc'][0].startswith("-") and self.remote['misc'][0][1] in ['o', 'h', 'v']:
					self.inv['rooms'][self.remote['receiver']][self.remote['misc'][1]]['mode'] = None

	def _reload(self, args):
		if len(args) == 1:
			importlib.reload(modules)
			response = "Success: Reloaded all submodules."
		elif len(args) == 2:
			if os.path.exists("%s/modules/%s.py" % (os.path.dirname(__file__), args[1])):
				importlib.reload(__import__('modules.' + args[1], globals(), locals(), fromlist = [], level = 1))
				response = "Success: Reloaded '%s' submodule." % args[1]
			else:
				response = "Failure: No such module '%s'." % args[1]
		elif len(args) > 2:
			affected, unaffected = [], []
			for module in args[1:]:
				if os.path.exists("%s/modules/%s.py" % (os.path.dirname(__file__), module)):
					importlib.reload(__import__('modules.' + module, globals(), locals(), fromlist = [], level = 1))
					affected.append(module)
				else:
					unaffected.append(module)
			if (len(args[1:]) - len(unaffected)) == len(args[1:]):
				response = "Success: Reloaded %s submodules." % ', '.join(args[1:])
			elif len(unaffected) < len(args[1:]):
				pl1 = "" if len(unaffected) == 1 else "s"
				pl2 = "was" if len(affected) == 1 else "were"
				response = "Partial: Could not reload %s submodule%s but %s %s ok." % (', '.join(unaffected), pl1, ', '.join(affected), pl2)
			else:
				response = "Failure: No such modules."
			del affected, unaffected

		self._sendq(("PRIVMSG", self.remote['sendee']), response)
