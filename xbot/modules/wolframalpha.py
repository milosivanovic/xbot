import urllib2
import lxml.etree

def wa(bot, args):
	if len(args) > 1:
		response = urllib2.urlopen("http://api.wolframalpha.com/v2/query?appid=%s&input=%s&format=plaintext" % (bot.config.get('general', 'wa_app_id'), urllib2.quote(' '.join(args[1:]))), timeout = 10)
		result = lxml.etree.parse(response)
		acceptable = [
			'Result', 'Results', 'Solution', 'Value', 'Name', 'Derivative', 'Indefinite integral', 'Distance',
			'Scientific notation', 'Truth table', 'Differential equation solution', 'Decimal form', 'Decimal approximation',
			'Exact result', 'Rational approximation', 'Geometric figure', 'Definition', 'Basic definition', 'Result for *',
			'Number length', 'Definitions', 'Unit conversions', 'Electromagnetic frequency range', 'IP address registrant',
			'Address properties', 'Web hosting information', 'Current age', 'Basic information', 'Latest result', 'Response',
			'Names and airport codes', 'Latest recorded weather *', 'Series information', 'Latest trade', 'Definitions of *',
			'Possible interpretation*', 'Lifespan', 'Cipher text', 'Statement', 'Events on *', 'Time span', 'Unicode block'
		]
		for title in acceptable:
			success = xml(result, title)
			if success: break
		failure = result.xpath("/queryresult[@success='false']")
		if success:
			return ''.join(success).encode('utf-8').strip()
		elif failure:
			return __import__('random').choice(['Are you a wizard?', 'You must be a wizard.', "Plong.", "I like bytes.", "Mmmm... chocolate...", "Oooh look, a boat.", 'Boob.'])
		else:
			return "No acceptable mathematical result."
	else:
		return "Usage: !%s <mathematical query>" % args[0]

def xml(result, title):
	if '*' in title:
		return result.xpath("/queryresult[@success='true']/pod[contains(@title, '%s')]/subpod/plaintext/text()" % title.replace("*", ""))
	else:
		return result.xpath("/queryresult[@success='true']/pod[@title='%s']/subpod/plaintext/text()" % title)