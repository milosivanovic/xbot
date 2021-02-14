import urllib.request
import urllib.error
import urllib.parse
import json
import re

from . import scanner

def search(bot, args):
	if len(args) >= 2:
		title = ""
		
		if args[1].startswith("cr="):
			expr = re.search('cr=([a-zA-Z]{2})$', args[1])
			if expr:
				country = expr.group(1).upper()
				if country == "CN":
					return "google.cn? hah."
			else:
				return "Invalid country code."
			terms = ' '.join(args[2:])
		else:
			country = ""
			terms = ' '.join(args[1:])
		result = urllib.request.urlopen("https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&gl=%s&q=%s" % (bot.config.get('module: googlesearch', 'api_key'), bot.config.get('module: googlesearch', 'custom_search_id'), country, urllib.parse.quote(terms)), timeout = 5)
		jsondata = json.load(result)
		try:
			url = jsondata['items'][0]['link']
		except KeyError:
			return "Your search did not return any results."
		if url.startswith("http://www.youtube.com/") or url.startswith("https://www.youtube.com/"):
			title = "\n" + scanner.scan(bot, url)
		if country:
			return "From %s only: %s%s" % (country, url, title)
		else:
			return "%s%s" % (url, title)

	else:
		return "Usage: !%s [cr=<2-letter country code>] <query>" % args[0]
