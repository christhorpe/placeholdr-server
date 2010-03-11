from google.appengine.ext import db

class Location(db.Model):
	lat = db.StringProperty()
	lon = db.StringProperty()
	viewcount = db.IntegerProperty(default=0)
	sectionlist = db.StringListProperty()


class Mark(db.Model):
	lat = db.StringProperty()
	lon = db.StringProperty()
	lockey = db.StringProperty()
	url = db.StringProperty()
	useragent = db.StringProperty()
	section = db.StringProperty()
	created_at = db.DateTimeProperty(auto_now_add=True)

