import urllib.request
import urllib.parse
import lxml.html
import re

def unicode_truncate(s, length, encoding='utf-8'):
	encoded = s.encode(encoding)[:length]
	return encoded.decode(encoding, 'ignore')

def etym(bot, args):
	if len(args) > 1:
		support = ['en', 'fr']
		if args[1].startswith('@'):
			lang = args[1][1:]
			if lang in support:
				query = ' '.join(args[2:])
			else:
				return "!%s: unsupported language (use: %s)" % (args[0], ','.join(support))
		else:
			lang = 'en'
			query = ' '.join(args[1:])

		if lang == 'en':
			url = 'http://www.etymonline.com/?term=%s' % urllib.parse.quote_plus(query)
			page = urllib.request.urlopen(url).read()
			result = lxml.html.fromstring(page).xpath("//div[@id='dictionary']/dl/dd//text()")
		elif lang == 'fr':
			url = 'http://www.cnrtl.fr/etymologie/%s' % urllib.parse.quote_plus(query)
			page = urllib.request.urlopen(url).read()
			result = lxml.html.fromstring(page).xpath("//div[@id='contentbox']//text()")
		if result:
			text = ''.join(result)
			overhead = len(url)
			if len(text) > (435-overhead):
				text = "%s... (%s)" % (unicode_truncate(text, 435-overhead), url)
			#return ' | '.join(line.strip() for line in lines.splitlines() if line)
			return re.sub('[\r\n]+', ' | ', re.sub(' +', ' ', text.strip()))
		return '!%s: no etymology found in "%s"' % (args[0], lang)
	return "!%s [@en|fr] <word>" % args[0]
