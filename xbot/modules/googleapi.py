import urllib2
import simplejson

def search(bot, args):
	if len(args) >= 2:
		title = ""
		
		if args[1].startswith("cr="):
			expr = __import__('re').search('cr=([a-zA-Z]{2})$', args[1])
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
		result = urllib2.urlopen("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&q=%s&gl=%s" % (urllib2.quote(terms), country), timeout = 5)
		jsondata = simplejson.load(result)
		try:
			url = jsondata['responseData']['results'][0]['unescapedUrl']
			if url.startswith("http://www.youtube.com/"):
				import scanner
				bot.remote['message'] = url
				title = "\n" + scanner.scan(bot)
			if country:
				return "From %s only: %s%s" % (country, url, title)
			else:
				return "%s%s" % (url, title)
		except IndexError:
			return "Your search did not return any results."
	else:
		return "Usage: !%s [cr=<2-letter country code>] <query>" % args[0]