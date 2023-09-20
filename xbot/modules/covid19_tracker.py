import urllib
import csv

def nzvax(bot, args):
	data = urllib.request.urlopen("https://insights.nzherald.co.nz/apps/2021/vaccine-progress-dhb/data/live.data").read().decode('utf8')
	lines = data.splitlines()
	reader = csv.reader(lines)
	next(reader, None)
	db = {rows[0].lower():rows[1:] for rows in reader}
	if len(args) == 1:
		chosen_dhb = "auckland"
	else:
		chosen_dhb = ' '.join(args[1:])
	try:
		entry = db[chosen_dhb.lower()]
	except KeyError:
		return "!%s: '%s' is not a valid DHB, available: %s" % (args[0], args[1], ', '.join(db.keys()))
	return "%s DHB: dose1 %.1f%%, dose2 %.1f%% (%d unvaccinated)" % (chosen_dhb.capitalize(), int(entry[1])/int(entry[0])*100, int(entry[2])/int(entry[0])*100, int(entry[0])-int(entry[2]))
