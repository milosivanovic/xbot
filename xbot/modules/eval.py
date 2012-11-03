import subprocess
import re

def parse(bot, args):
	command = ' '.join([arg for arg in args[1:]])
	arguments = ['python', '-c', command]
	result = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
	
	if len(result.split('\n')) > 4 or len(result) > 445:
		service = ['wgetpaste']
		for n in range(2):
			p = subprocess.Popen(service, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			paste = p.communicate(input=">>> %s\n\n%s" % (command, result))[0]
			try:
				return re.findall('(http://.*)', paste, re.S)[0]
			except IndexError:
				service = ['curl', '-F', 'sprunge=<-', 'http://sprunge.us']
		return "!%s: error pasting output." % args[0]
	else:	
		return result