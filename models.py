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
	processed = db.BooleanProperty(default=False)


class Activity(db.Model):
	mark = db.ReferenceProperty()
	device = db.StringProperty()
	title = db.StringProperty()
	location = db.StringProperty()
	lockey = db.StringProperty()
	created_at = db.DateTimeProperty()

