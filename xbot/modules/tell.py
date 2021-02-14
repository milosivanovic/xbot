def answer(bot, args):
	library = {
		'yourself': "I'm an awesome lil bot n.n",
		'irc': "IRC stands for Internet Relay Chat, and you're using it this very minute! :O",
		'enter': "Stop pressing the Enter key so much! Grrrrr. Rage rage rage.",
		'sleep': "Sleep's pretty good, yep. You should do it sometime.",
		'bacon': "Lemme tell you something. Bacon, is good for you. (see http://www.youtube.com/watch?v=2T_obaO46Bo for details.)",
		'cubestormer': "The CubeStormer II is an awesome LEGO Mindstorms\x99 NXT robot that can solve Rubik's Cubes in a matter of seconds. See http://www.youtube.com/watch?v=_d0LfkIut2M for a video demonstration.",
		'ql': "Quantum Levitation is fecking awesome. See http://www.youtube.com/watch?v=Ws6AAhTw7RA and http://www.youtube.com/watch?v=VyOtIsnG71U",
		'intelligence': 'sure is the most intelligent person in ##francophonie',
		'tsenko': "le rap de tsenko: https://transfer.sh/MQTnN/tsenko-mixtape.opus"
	}
	if len(args) >= 4:
		if args[2] == "about":
			what = ' '.join(args[3:]).lower()
			if library.get(what):
				if bot.inv['rooms'].get(bot.remote['receiver']):
					if args[1].lower() in [nick.lower() for nick in bot.inv['rooms'].get(bot.remote['receiver'])]:
						return "%s: %s" % (args[1], library[what])
					else:
						return "%s: %s isn't in this channel." % (bot.remote['nick'], args[1])
				else:
					return "Triggering this command privately is not allowed."
			else:
				return None
	return "Usage: !%s <nick> about <%s>" % (args[0], '|'.join(list(library.keys())))
