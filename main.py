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
from django.utils import simplejson

import proxy
import api
import helpers
import models


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
		marks = models.Mark.all().order('-created_at').fetch(10)
		locations = models.Location.all().order('-viewcount').fetch(10)
		template_values = {
			"centre_point": "",
			"marks": marks,
			"locations": locations,
		}
		helpers.render_template(self, "views/homeview.html", template_values)


class TestFeeds(webapp.RequestHandler):
	def get(self):
		request = urlfetch.fetch(url="http://bonnier-scraper.appspot.com/api/imageitems?format=xml", method=urlfetch.GET)
		self.response.out.write(request.content)


def main():
	application = webapp.WSGIApplication([
		('/', HomeHandler),
		('/proxy', ProxyHandler),
		('/api/mark', api.MarkHandler),
		('/get/item', TestFeeds),
		], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
