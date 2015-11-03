import urllib, urllib2
import json
import re
from bs4 import BeautifulSoup

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
			'prop': 'extracts|pageprops',
			'exintro': '',
			'explaintext': '',
			'titles': query,
			'redirects': ''
		}
		params_full = {
			'format': 'json',
			'action': 'parse',
			'prop': 'text',
			'page': query,
			'redirects': ''
		}
		data = json.load(urllib2.urlopen('https://%s.wikipedia.org/w/api.php?%s' % (lang, urllib.urlencode(params_extract)), timeout = 5))
		try:
			response = data['query']['pages']
			for page_id, page_data in response.iteritems():
				try:
					page_data['pageprops']['disambiguation']
					data = json.load(urllib2.urlopen('https://%s.wikipedia.org/w/api.php?%s' % (lang, urllib.urlencode(params_full)), timeout = 5))
					for page_id_2, page_data_2 in data['parse'].iteritems():
						soup = BeautifulSoup(page_data_2['*'])
						lis = []
						links = []
						for uls in soup.find_all('ul'):
							for li in uls.find_all('li'):
								if li.find('ul'):
									break
								lis.append(li)
						for link in lis:
							if 'toc' not in str(link.get('class')):
								links.append(link.text)
#							if link.get('title'):
#								links.append(link['title'])
						text = ' | '.join(links)
						if len(text) > 440:
							text = "%s..." % unicode_truncate(text, 440)
						return text.encode('utf-8')
				except KeyError:
					pass
				text = re.sub('\n+', ' | ', page_data['extract'].strip())
				if len(text) > 440:
					text = "%s..." % unicode_truncate(text, 440)
				return text.encode('utf-8')
		except KeyError:
			return '!%s: no such article in "%s"' % (args[0], lang)
	else:
		return "Usage: !%s [@lang] topic" % args[0]
