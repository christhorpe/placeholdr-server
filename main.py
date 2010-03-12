#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
import os



from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.api import memcache

from django.utils import simplejson



import proxy
import api
import helpers
import models
import yql

class ProxyHandler(webapp.RequestHandler):
	def get(self):
		if self.request.get("url"):
			url = self.request.get("url")
		else:
			url = "http://www.dn.se/"
		proxied_page = proxy.get_dndotse(url)
		template_values = {
			"proxied_page": proxied_page,
			"url":url
		}
		helpers.render_template(self, "views/proxyview.html", template_values)


class HomeHandler(webapp.RequestHandler):
	def get(self):
		activities = models.Activity.all().order('-created_at').fetch(10)
		locations = models.Location.all().order('-viewcount').fetch(10)
		template_values = {
			"centre_point": "",
			"activities": activities,
			"locations": locations,
		}
		helpers.render_template(self, "views/homeview.html", template_values)


def get_section_item(url):
	sections = [
			{"url":"http://www.dn.se/", "label":"Forstasidan"},
			{"url":"http://www.dn.se/bostad/", "label":"Bostad"},
			{"url":"http://www.dn.se/nyheter/sverige/", "label":"Sverige"},
			{"url":"http://www.dn.se/nyheter/valet2010/", "label":"Valet2010"},
			{"url":"http://www.dn.se/nyheter/varlden/", "label":"Varlden"},
			{"url":"http://www.dn.se/nyheter/vetenskap/", "label":"Vetenskap"},
			{"url":"http://www.dn.se/sthlm/", "label":"STHLM"},
			{"url":"http://www.dn.se/sthlm/sthlmfordjupning/", "label":"STHLM Fordjupning"},
			{"url":"http://www.dn.se/ekonomi/", "label":"Ekonomi"},
			{"url":"http://www.dn.se/ekonomi/din-ekonomi/", "label":"Din Ekonomi"},
			{"url":"http://www.dn.se/sport/", "label":"Sport"},
			{"url":"http://www.dn.se/sport/fotboll/", "label":"Fotboll"},
			{"url":"http://www.dn.se/sport/ishockey/", "label":"Ishockey"},
			{"url":"http://www.dn.se/sport/os-vancouver/", "label":"OS2010"},
			{"url":"http://www.dn.se/kultur-noje/", "label":"Kulture"},
			{"url":"http://www.dn.se/dnbok/", "label":"DN Bok"},
			{"url":"http://www.dn.se/kultur-noje/debatt-essa/", "label":"Kulturdebatt"},
			{"url":"http://www.dn.se/kultur-noje/essa/", "label":"Essa"},
			{"url":"http://www.dn.se/kultur-noje/film-tv/", "label":"Film TV"},
			{"url":"http://www.dn.se/kultur-noje/konst-form/", "label":"Konst Form"},
			{"url":"http://www.dn.se/kultur-noje/musik/", "label":"Music"},
			{"url":"http://www.dn.se/kultur-noje/scen/", "label":"Scen"},
			{"url":"http://www.dn.se/spel/", "label":"Spel"},
			{"url":"http://www.dn.se/opinion/", "label":"Opinion"},
			{"url":"http://www.dn.se/opinion/debatt/", "label":"Debatt"},
			{"url":"http://www.dn.se/opinion/huvudledare/", "label":"Huvudledare"},
			{"url":"http://www.dn.se/opinion/signerat/", "label":"Signerat"},
			{"url":"http://www.dn.se/opinion/kolumner/", "label":"Kolumner"},
			{"url":"http://www.dn.se/resor/", "label":"Resor"},
			{"url":"http://www.dn.se/mat-dryck/", "label":"Mat Dryck"},
			{"url":"http://www.dn.se/mat-dryck/reportage/", "label":"Mat Dryck Reportage"},
			{"url":"http://www.dn.se/mat-dryck/dryck/", "label":"Mat Dryck Dryck"},
			{"url":"http://www.dn.se/livsstil/", "label":"Livsstil"},
			{"url":"http://www.dn.se/livsstil/intervjuer/", "label":"Livsstil Intervjuer"},
			{"url":"http://www.dn.se/livsstil/livsstilsreportage/", "label":"Livsstil Reportage"},
			{"url":"http://www.dn.se/livsstil/halsa/", "label":"Livsstil Halsa"},
			{"url":"http://www.dn.se/livsstil/relationer/", "label":"Livsstil Relationer"},
			{"url":"http://www.dn.se/livsstil/trend/", "label":"Livsstil Trend"},
			{"url":"http://www.dn.se/insidan/", "label":"Insidan"},
			{"url":"http://www.dn.se/livsstil/livsstilsbloggar/", "label":"Livsstil Bloggar"},
		]
	for section in sections:
		if url == section['url']:
			return section['label']

def get_item(url):
	item = memcache.get(url)
	if not item:
		title = False
		title = get_section_item(url)
		if not title:
			request = urlfetch.fetch(url="http://bonnier-scraper.appspot.com/api/item?url=%s" % url, method=urlfetch.GET)
			try:
				json = simplejson.loads(request.content)
				item = {
						"title": json['title'],
						"url": url,
						}
				if "imgurl" in json:
					item["imgurl"] = "http://bonnier-scraper.appspot.com/api/image?url=%s" % url
				if "byline" in json:
					item["byline"] = json['byline']
				if "description" in json:
					item["description"] = json['description']
			except:
				item = False
		else:
				item = {
					"title": title,
					"url": url
				}
		if item:
			memcache.add(url, item, 10000)
	return item



def get_location(lockey, lat, lon):
	location = memcache.get(lockey)
	if not location:
		query = "select * from geo.places where woeid in (select place.woeid from flickr.places where lat='" + lat +"' and  lon='"+ lon +"')";
		result = helpers.do_yql(query)
		try:
			yql_location = result['query']['results']['place']
			location = yql_location['name'] + ", " + yql_location['country']['content']
			memcache.add(lockey, location, 10000)
		except:
			location = "not found"
	return location



def get_device(useragent):
	if useragent.find("iPhone") > -1:
		return "iPhone"
	elif useragent.find("iPad") > -1:
		return "iPad"
	else:
		return "other"



class ProcessActivity(webapp.RequestHandler):
	def get(self):
		key = self.request.get("key")
		if key:
			mark = models.Mark.get(key)
			item = get_item(mark.url)
			location = get_location(mark.lockey, mark.lat, mark.lon)
			device = get_device(mark.useragent)
			akey = str("a_" + key)
			if item:
				activity = models.Activity.get_or_insert(akey, mark=mark, device=device, title=item['title'], location=location, lockey=mark.lockey, created_at=mark.created_at)
				self.response.out.write(item['title'])
				self.response.out.write("<br />")
				self.response.out.write(location)
				self.response.out.write("<br />")
				self.response.out.write(device)
				mark.processed = True
				mark.put()
			else:
				self.response.out.write("broken item for " + mark.url)


class ProcessActivityQueue(webapp.RequestHandler):
	def get(self):
		marks = models.Mark.all()
		for mark in marks:
			taskqueue.add(url='/actions/activity/process', params={'key': str(mark.key())}, method='GET')
			


def main():
	application = webapp.WSGIApplication([
		('/', HomeHandler),
		('/proxy', ProxyHandler),
		('/api/mark', api.MarkHandler),
		('/actions/activity/process', ProcessActivity),
		('/process/activitystream', ProcessActivityQueue)
		], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
