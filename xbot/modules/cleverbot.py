import urllib, urllib2
import hashlib

class CleverBot(object):

	def __init__(self):
		self.params = {
			'start': 'y', 'icognoid': 'wsf', 'fno': '0', 'sub': 'Say', 'islearning': '1', 'cleanslate': 'false'
		}
		self.vars = [
			'sessionid', 'logurl', 'vText8', 'vText7', 'vText6', 'vText5', 'vText4', 'vText3', 'vText2', 'prevref',
			'asbotname', 'emotionaloutput', 'ttsLocMP3', 'ttsLocTXT', 'ttsLocTXT3', 'ttsText', 'lineRef', 'lineURL',
			'linePOST', 'lineChoices', 'lineChoicesAbbrev', 'typingData', 'divert'
		]
	
	def query(self, thought):
		self.params['stimulus'] = thought
		data = urllib.urlencode(self.params)
		data += '&icognocheck=' + hashlib.md5(data[9:29]).hexdigest()
		responses = urllib2.urlopen("http://cleverbot.com/webservicemin", data, timeout = 30).read().split('\r')
		
		for n in range(len(responses)):
			try: self.params[self.vars[n]] = responses[n+1]
			except IndexError: pass
		
		return self.params['ttsText']