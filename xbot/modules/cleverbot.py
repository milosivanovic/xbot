import urllib.request
import urllib.parse
import hashlib
import http.cookiejar

class CleverBot(object):

	def __init__(self):
		self.url = 'https://www.cleverbot.com/webservicemin?uc=UseOfficialCleverbotAPI&'
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
		self.vars = {
			'stimulus': '',
			'cb_settings_language': 'en',
			'cb_settings_scripting': 'no',
			'islearning': 1,
			'icognoid': 'wsf'
		}
		# set cookies by visiting the main page first
		self.opener.open('https://www.cleverbot.com/')
	
	def query(self, thought):
		self.vars['stimulus'] = thought
		data = urllib.parse.urlencode(self.vars)
		md5_digest = hashlib.md5(data[7:33].encode('utf8')).hexdigest()
		data += '&icognocheck=' + md5_digest
		response = self.opener.open(self.url, data.encode('utf8')).read().decode('utf8')
		values = response.splitlines()
		self.vars['sessionid'] = values[1]
		self.vars['vText8'] = values[3]
		self.vars['vText7'] = values[4]
		self.vars['vText6'] = values[5]
		self.vars['vText5'] = values[6]
		self.vars['vText4'] = values[7]
		self.vars['vText3'] = values[8]
		self.vars['vText2'] = values[9]

		return values[0]
