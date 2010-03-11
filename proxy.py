import re

from google.appengine.api import urlfetch
from google.appengine.api import memcache

def get_dndotse(url):
	outtext = memcache.get(url)
	if not outtext:
		response = urlfetch.fetch(url=url, method=urlfetch.GET)
		rawresponse = response.content
		nodomainpattern = r'''<a href="([^"]+)">([^>]+)</a>'''
		domainpattern = r'''<a href="http://test.placeholdr.me/proxy?url=http://www.dn.se\1">\2</a>'''
		domainedresponse = re.sub(nodomainpattern, domainpattern, rawresponse)
		nodomainimagepattern = r'''img src="([^"]+)"'''
		domainimagepattern = r'''img src="http://www.dn.se\1"'''
		outtext = re.sub(nodomainimagepattern, domainimagepattern, domainedresponse).replace("http://www.dn.sehttp://www.dn.se", "http://www.dn.se")
		memcache.add(url, outtext, 300)
	return outtext

