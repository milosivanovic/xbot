import urllib2
import lxml.etree
import re

def get_results(bot, args):
	tree = lxml.etree.parse('http://www.lottoresults.co.nz/', lxml.etree.HTMLParser())
	images = tree.xpath("//td/img[contains(@src, 'img/lotto/')]")
	draw = tree.xpath("//input[@name='draw']")[0].get('value')
	results = [re.match('img/lotto/([0-9]+)\.gif', result.get('src')).group(1) for result in images]
	
	lotto = results[0:6]
	bonus_ball = results[6]
	strike = results[7:11]
	powerball = results[11]
	
	return "Weekly draw #%d as follows\nLotto: %s, bonus %d, powerball %d. Strike order: %s." % (int(draw), ', '.join(lotto), int(bonus_ball), int(powerball), ', '.join(strike))