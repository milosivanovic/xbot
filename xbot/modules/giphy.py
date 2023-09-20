import urllib.request
import json

def search(bot, args):
	if len(args) > 1:
		result = urllib.request.urlopen('https://api.giphy.com/v1/gifs/search?api_key=%s&q=%s&limit=25&offset=0&rating=g&lang=en' % (bot.config.get('module: giphy', 'api_key'), urllib.parse.quote(''.join(args[1:]))))
		jsondata = json.loads(result.read().decode('utf8'))
		if 'data' in jsondata:
			if len(jsondata['data']) > 1:
				return "https://i.giphy.com/media/%s/giphy.gif" % jsondata['data'][0]['id']
				#return jsondata['data'][0]['images']['original']['url']

		return "!%s: No GIF found." % args[0]

	return "Usage: !%s <query>" % args[0]
