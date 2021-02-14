import urllib.request
import urllib.parse
import json
import re

def unicode_truncate(s, length, encoding='utf-8'):
	encoded = s.encode(encoding)[:length]
	return encoded.decode(encoding, 'ignore')

def ud(bot, args):
	if len(args) > 1:
		support = ['en']
		if args[1].startswith('@'):
			lang = args[1][1:]
			if lang in support:
				query = ' '.join(args[2:])
			else:
				return "!%s: unsupported language (use: %s)" % (args[0], ','.join(support))
		else:
			lang = 'en'
			query = ' '.join(args[1:])

		result = None
		friendly_url = "http://www.urbandictionary.com/define.php?term=%s" % urllib.parse.quote_plus(query)

		if lang == 'en':
			url = 'http://api.urbandictionary.com/v0/define?term=%s' % urllib.parse.quote_plus(query)
			json_text = urllib.request.urlopen(url).read()
			json_obj = json.loads(json_text)
			try:
				result = json_obj['list'][0]['definition']
			except IndexError:
				pass
		if result:
			text = ''.join(result)
			overhead = len(friendly_url)
			if len(text) > (435-overhead):
				text = "%s... (%s)" % (unicode_truncate(text, 435-overhead), friendly_url)
			return re.sub('[\r\n]+', ' | ', re.sub(' +', ' ', text.strip()))
		return '!%s: no urban dictionary result found in "%s"' % (args[0], lang)
	return "Usage: !%s [@en] <word>" % args[0]
