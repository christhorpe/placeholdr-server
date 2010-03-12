import os
import yql

from google.appengine.ext.webapp import template


def do_yql(query):
	y = yql.Public()
	result = y.execute(query)
	return result


def render_template(self, end_point, template_values):
	path = os.path.join(os.path.dirname(__file__), "templates/" + end_point)
	response = template.render(path, template_values)
	self.response.out.write(response)
