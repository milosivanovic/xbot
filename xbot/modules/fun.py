from functools import reduce
import random

def twss(bot, args):
	if len(args) > 1:
		quote = ' '.join(args[1:])
		if quote.startswith('"') and quote.endswith('"'):
			return "%s <- that's what she said." % quote
		else:
			return 'Usage: !%s "<quote>"' % args[0]
	return "That's what she said."

def spin(bot, args):
	nicks = bot.inv['rooms'].get(bot.remote['receiver'])
	if nicks:
		if len(nicks) > 2:
			message = ' '.join(args[1:])
			if not message:
					message = "nothing"
			if message.lower() != bot.nick.lower():
				_nicks = list(nicks)
				_nicks.remove(bot.remote['nick'])
				_nicks.remove(bot.nick)
				winner = random.choice(_nicks)
				return "The winner of %s is %s. Congratulations %s!" % (message, winner, winner)
			else:
				return "You want to spin me? Ok. Wheeeeeeee~"
		else:
			return "Not enough winrars!"
	else:
		return "Triggering this command privately is not allowed."

def cookie(bot, args):
	if len(args) == 2:
		nicks = bot.inv['rooms'].get(bot.remote['receiver'])
		if nicks:
			if args[1].lower() in [nick.lower() for nick in nicks]:
				if args[1].lower() != bot.name.lower():
					return "\x01ACTION gives %s a cookie.\x01" % args[1]
				else:
					return "OM NOM NOM NOM."
			else:
				return "Who?"
		else:
			return "Triggering this command privately is not allowed."
	else:
		return "Usage: !%s <nick>" % args[0]

def choose(bot, args):
	import random
	args_ = list(set(' '.join([arg.lower() if arg.lower() == 'or' else arg for arg in args[1:]]).split(' or ')))
	args__ = list(set([arg.lower() for arg in args_]))
	if len(args_) > 1 and len(args_) == len(args__):
		answer = random.choice([
			'Defs', 'Totes', 'I reckon', 'Why not', 'I like *', 'DEFINITELY',
			'Without a doubt', 'Always', 'A must-choose: *', 'You could ^',
			'I recommend *', 'Perhaps', 'Blimey,', 'How about *', 'HAHA,',
			'I say', 'Something tells me', 'Try *', 'Go with *', 'I highly recommend *'
		])
		choice = random.choice(args_)
		intermediary = "choose " if random.random() > 0.5 else ''
		if '*' in answer:
			intermediary = ''
			answer = answer[:-2]
		elif '^' in answer:
			intermediary = "choose "
			answer = answer[:-2]
		if choice.endswith("?") and len(choice) > 1: choice = choice[:-1]
		return "%s %s%s." % (answer, intermediary, choice)
	else:
		return "Usage: !%s <item 1> or <item 2> [or <item n>] where 1 != 2 != n" % args[0]

def m8b(bot, args):
	if len(args) > 1:
		responses = [
			"It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Signs point to yes.", "Yes.",
			"Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
			"Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
		]
		return random.choice(responses)
	else:
		return "Usage: !%s <herp>" % args[0]

def ghetto(bot, args):
	if len(args) == 2:
		real_name = args[1].lower()
		ghetto_name = ""

		table = {
					'a': 'sha', 'b': 'ni', 'c': 'ki', 'd': 'que',
					'e': 'nay', 'f': 'qui', 'g': 'ti', 'h': 'la',
					'i': 'kay', 'j': 'ri', 'k': 'barack', 'l': 'obama',
					'm': 'di', 'n': 'ta', 'o': 'ee', 'p': 'ray',
					'q': 'cli', 'r': 'gurl', 's': 'na', 't': 'qua',
					'u': 'kwa', 'v': 'ise', 'w': 'fi', 'x': 'quee',
					'y': 'mi', 'z': 'si'
		}

		for letter in real_name:
			try: ghetto_name += table[letter] + "-"
			except KeyError: return "Invalid name."

		return ghetto_name[:-1]

	return "Usage: !%s <first name>" % args[0]

def sorting_hat(bot, args):
	if len(args) == 2:
		nicks = bot.inv['rooms'].get(bot.remote['receiver'])
		if nicks:
			if args[1].lower() in [nick.lower() for nick in nicks]:
				houses = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherine']
				return houses[sum(ord(c) for c in args[1]) % 4] + '!'
			else:
				return "But they're not here!"
		else:
			return "It's a secret."

	return "Usage: !%s <nick>" % args[0]

def lotto(bot, args):
	import random
	balls = random.sample(list(range(1, 41)), 7)
	return "Winning lotto numbers are: %s & bonus ball %d with powerball %d" % (', '.join(str(s) for s in balls[:-1]), balls[6], random.randint(1, 10))

def keygen(bot, args):
	import string
	import random
	return '-'.join([''.join([random.choice(string.ascii_uppercase+string.digits) for n in range(5)]) for n in range(5)])

def benis(bot, args):
	import random
	import unicodedata
	import re
	if len(args) > 0:
		if len(args) > 1:
			s = ' '.join(args[1:])
		else:
			s = bot.previous['message']
		return reduce(lambda acc, f: f(acc), [
			lambda s: s.lower(),
			lambda s: unicodedata.normalize('NFKD', s),
			lambda s: s.replace('x', 'cks'),
			lambda s: re.sub(r'ing','in', s),
			lambda s: re.sub(r'you', 'u', s),
			lambda s: re.sub(r'oo', lambda _: random.randint(1, 5) * 'u', s),
			lambda s: re.sub(r'\w\0', lambda x: random.randint(1, 2) * x.group(0)[0], s),
			lambda s: re.sub(r'ck', lambda _: random.randint(1, 5) * 'g', s),
			lambda s: re.sub(r'(t+)(?=[aeiouys]|\b)', lambda x: 'd' * len(x.group(1)), s),
			lambda s: s.replace('p', 'b'),
			lambda s: re.sub(r'\bthe\b', 'da', s),
			lambda s: re.sub(r'\bc', 'g', s),
			lambda s: re.sub(r'\bis\b', 'are', s),
			lambda s: re.sub(r'c+(?![eiy])', lambda _: random.randint(1, 5) * 'g', s),
			lambda s: re.sub(r'k+(?=[aeiouy]|\b)', lambda _: random.randint(1, 5) * 'g', s),
			lambda s: re.sub(r'([?!.]|$)+', lambda x: (x.group(0) * random.randint(2, 5)) + " " + "".join((":" * random.randint(1, 2)) + ("D" * random.randint(1, 4)) for _ in range(random.randint(2, 5))), s),
		], s)
	else:
		return "Usage: !%s <English sentence>" % args[0]

def nab(bot, args):
	result = "TU M'ENTENDS? :@"
	if len(args) > 1:
		nicks = bot.inv['rooms'].get(bot.remote['receiver'])
		nick_arguments = args[1:]
		for nick_arg in nick_arguments:
			if nick_arg.lower() not in [nick.lower() for nick in nicks]:
				return "nn"
		if len(args) == 2:
			return "%s: TU M'ENTENDS? :@" % ', '.join(nick_arguments)
		else:
			return "%s: VOUS M'ENTENDEZ? :@" % ', '.join(nick_arguments)
	return result

def frites(bot, args):
	result = "ferme un peu ta gueule, va m'faire un steak frite ! (https://transfer.sh/HCwNv/frites.ogg)"
	if len(args) > 1:
		nicks = bot.inv['rooms'].get(bot.remote['receiver'])
		nick_arguments = args[1:]
		for nick_arg in nick_arguments:
			if nick_arg.lower() not in [nick.lower() for nick in nicks]:
				return "nn"
		if len(args) == 2:
			return "%s: ferme un peu ta gueule, va m'faire un steak frite ! (https://transfer.sh/HCwNv/frites.ogg)" % ', '.join(nick_arguments)
		else:
			return "!%s: FRITES ET POUR UN SEUL!" % args[0]
	return result

def monsieurp(bot, args):
	return "\x01ACTION fait sauter la fesse de monsieurp\x01"

def sysinfo(bot, args):
	import os
	uname = os.popen('uname -a')
	uname_result = uname.read()
	uname.close()

	uptime = os.popen('uptime')
	uptime_result = uptime.read()
	uptime.close()
	return '\n'.join([uname_result, uptime_result])
