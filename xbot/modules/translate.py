import urllib, urllib2
import json
import HTMLParser

def translate(bot, args):
	if len(args) > 2:
		if "|" not in args[1]:
			return "Usage: !%s <from|to> <msg>" % args[0]
		lang_from, lang_to = args[1].split("|")
		query = ' '.join(args[2:])
		data = json.load(urllib2.urlopen('https://www.googleapis.com/language/translate/v2?%s' % urllib.urlencode({'key': bot.config.get('module: translate', 'gapi_key'), 'q': query, 'source': lang_from, 'target': lang_to}), timeout = 5))
		try:
			response = data['data']['translations'][0]['translatedText']
			parser = HTMLParser.HTMLParser()
			return parser.unescape(response).encode('utf-8')
		except ValueError:
			return '!%s: le derp' % args[0]
	else:
		return "Usage: !%s <from|to> <msg>" % args[0]
