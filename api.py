import os

from google.appengine.ext import webapp
from google.appengine.api.labs import taskqueue

import models


class MarkHandler(webapp.RequestHandler):
	def get(self):
		mark = models.Mark()
		mark.lat = self.request.get("lat")[0:7]
		mark.lon = self.request.get("lon")[0:7]
		lockey = "l_" + mark.lat[0:7].replace(".", "") + mark.lon[0:7].replace(".", "")
		mark.lockey = lockey
		mark.url = self.request.get("url")
		mark.useragent = os.environ['HTTP_USER_AGENT']
		urlend = mark.url.replace("http://www.dn.se/", "")
		if len(urlend) > 0:
			list = urlend.split("/")
			mark.section = list[0]
		else:
			mark.section = "home"
		mark.put()
		location = models.Location.get_or_insert(lockey, lat=mark.lat[0:7], lon= mark.lon[0:7], viewcount=0, sectionlist=[mark.section])
		location.viewcount += 1
		if mark.section not in location.sectionlist:
			location.sectionlist.append(mark.section)
		location.put()
		taskqueue.add(url='/actions/activity/process', params={'key': mark.key}, method='GET')
		self.response.out.write("ok")



