import urllib2
import lxml.etree

def wa(bot, args):
	if len(args) > 1:
		response = urllib2.urlopen("http://api.wolframalpha.com/v2/query?appid=%s&input=%s&format=plaintext&ip=103.250.91.91" % (bot.config.get('module: wolframalpha', 'wa_app_id'), urllib2.quote(' '.join(args[1:]))), timeout = 20)
		result = lxml.etree.parse(response)
		acceptable = [
			'Result', 'Results', 'Solution', 'Value', 'Name', 'Derivative', 'Indefinite integral', 'Distance', 'Current result*',
			'Scientific notation', 'Truth table', 'Differential equation solution', 'Decimal form', 'Decimal approximation',
			'Exact result', 'Rational approximation', 'Geometric figure', 'Definition', 'Basic definition', 'Result for *',
			'Number length', 'Definitions', 'Unit conversions', 'Electromagnetic frequency range', 'IP address registrant',
			'Address properties', 'Web hosting information', 'Current age', 'Basic information', 'Latest result', 'Response',
			'Names and airport codes', 'Latest recorded weather *', 'Series information', 'Latest trade', 'Definitions of *',
			'Possible interpretation*', 'Lifespan', 'Cipher text', 'Statement', 'Events on *', 'Time span', 'Unicode block',
			'Eclipse date', 'Total eclipse*', 'Solar wind', 'Weather forecast for *', 'Notable events in *', 'Events on *', 'Basic elemental properties',
			'Possible sequence identification', 'Length of data', 'Properties', 'Approximate results', 'Summary', 'Nearest named HTML colors',
			'Alternate form', 'Estimated result', 'Estimated results'
		]
		for title in acceptable:
			success = xml(result, title)
			if success: break
		failure = result.xpath("/queryresult[@success='false']")
		if success:
			success = success.replace("\:", "\u")
			return success.encode('utf-8').replace("Wolfram|Alpha", bot.name).replace("Stephen Wolfram", "Milos Ivanovic").strip()
		elif failure:
			alternatives = result.xpath("/queryresult/relatedexamples/relatedexample[@input]")
			if alternatives:
				return "Query not understood; suggestion%s: %s" % ('s' if len(alternatives) > 1 else '', ' | '.join([alt.values()[0].strip() for alt in alternatives]))
			else:
				return __import__('random').choice(['Are you a wizard?', 'You must be a wizard.', "Plong.", "I like bytes.", "Mmmm... chocolate...", "Oooh look, a boat.", 'Boob.'])
		else:
			return "No acceptable mathematical result."
	else:
		return "Usage: !%s <mathematical query>" % args[0]

def xml(result, title):
	if '*' in title:
		result = '\n'.join(result.xpath("/queryresult[@success='true']/pod[contains(@title, '%s')]/subpod/plaintext/text()" % title.replace("*", "")))
	else:
		result = '\n'.join(result.xpath("/queryresult[@success='true']/pod[@title='%s']/subpod/plaintext/text()" % title))
	if len(result) > 445:
		return "!calc: possible flood. Result cancelled."
	else:
		return result
