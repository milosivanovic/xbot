import urllib.request
import urllib.parse
import json
import re

def unicode_truncate(s, length, encoding='utf-8'):
	encoded = s.encode(encoding)[:length]
	return encoded.decode(encoding, 'ignore')

def wiki(bot, args):
	if len(args) > 1:
		wikipedias = ['en', 'sv', 'de', 'nl', 'fr', 'war', 'ru', 'ceb', 'it', 'es', 'vi', 'pl', 'ja', 'pt', 'zh', 'uk', 'ca', 'fa', 'sh', 'no', 'ar', 'fi', 'id', 'hu', 'ro', 'cs', 'mi', 'ko']
		if args[1].startswith('@'):
			lang = args[1][1:]
			if lang in wikipedias:
				query = ' '.join(args[2:])
			else:
				return "!%s: unsupported language (use: %s)" % (args[0], ','.join(wikipedias))
		else:
			lang = 'en'
			query = ' '.join(args[1:])

		params_extract = {
			'format': 'json',
			'action': 'query',
			'prop': 'extracts',
			'exintro': '',
			'explaintext': '',
			'titles': query,
			'redirects': '1'
		}
		data = json.load(urllib.request.urlopen('https://%s.wikipedia.org/w/api.php?%s' % (lang, urllib.parse.urlencode(params_extract)), timeout = 5))
		try:
			response = data['query']['pages']
		except KeyError:
			return '!%s: no such article in "%s"' % (args[0], lang)

		for page_id, page_data in response.items():
			if page_id == "-1":
				return '!%s: no such article in "%s"' % (args[0], lang)
			text = re.sub('\n+', ' | ', page_data['extract'].strip())
			if len(text) > 440:
				text = "%s..." % unicode_truncate(text, 440)
			return text
	else:
		return "Usage: !%s [@lang] topic" % args[0]
