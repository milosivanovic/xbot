import dns.resolver, dns.reversename
import re

def lookitup(domain, type):
	if type == "A" or type == "AAAA":
		if re.search("^(?:[\w.-]+)(?<!\.)(?:\.[a-zA-Z]{2,6})+\.?$", domain):
			try:
				return dns.resolver.query(domain, type)
			except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
				return False
	elif type == "PTR":
		if re.search("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", domain) or re.search("^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$", domain):
				try:
					return dns.resolver.query(dns.reversename.from_address(domain), type)
				except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
					return False
	elif type:
		try:
			return dns.resolver.query(domain, type)
		except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
			return False
	return -1

def lookup(bot, args):
	usage = "Usage: !%s [-6 (IPv6), -r (rDNS)] <server>" % args[0]
	
	if len(args) in [2, 3]:
		addresses = None
		
		if len(args) == 2:
			host = args[1]
			addresses = lookitup(host, "A")
		elif len(args) == 3:
			host = args[2]
			if args[1] == "-6":
				addresses = lookitup(host, "AAAA")
			elif args[1] == "-r":
				addresses = lookitup(host, "PTR")
			else:
				return usage
			
		if addresses != -1:
			if addresses:
				plural = "others" if len(addresses) > 2 else "other"
				others = " (%s %s)" % (len(addresses), plural) if len(addresses) > 1 else ''
				return "Address: %s%s" % (addresses[0] if not str(addresses[0]).endswith(".") else str(addresses[0])[:-1], others)
			else:
				return "%s: NXDOMAIN" % host
		else:
			return "Invalid host for this type of lookup."
	else:
		return usage

def wiki(bot, args):
	if len(args) > 0:
		result = lookitup('%s.wp.dg.cx' % '_'.join(args[1:]), 'TXT')
		if result:
			result = str(result[0])
			return "^NOTICE %s" % ''.join(result.split('"'))
		else:
			return "No such article found."
		
	return "Usage: !%s <article>" % args[0]