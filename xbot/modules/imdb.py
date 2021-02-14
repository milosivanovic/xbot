import urllib.request
import urllib.parse
import json

def info(bot, args):
	if len(args) > 1:
		title = ' '.join(args[1:])
		data = json.load(urllib.request.urlopen('http://www.imdbapi.com/?%s' % urllib.parse.urlencode({'t': title}), timeout = 45))
		if 'Plot' in data:
			response = "%s (%s): %s\n%s, %s/10, %s. %s" % (data['Title'], data['Year'], data['Plot'],
															data['Rated'] if data['Rated'] != 'N/A' else 'Unrated',
															data['imdbRating'] if data['imdbRating'] != 'N/A' else '?',
															data['Genre'], 'http://www.imdb.com/title/%s/' % data['imdbID'])
			return response
		else:
			return '!%s: No such movie found.' % args[0]
	else:
		return "Usage: !%s <movie title>" % args[0]
