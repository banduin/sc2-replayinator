from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
import boto
import settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///tmp/test.db'
db = SQLAlchemy(app)

class Replay(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	key = db.Column(db.String(20), unique=True)
	hash = db.Column(db.String(40), unique=True)
	original_filename = db.Column(db.String(512))
	filepath = db.Column(db.String(1024))

	def __init__(self, filename, hash):
		self.original_filename = filename
		self.hash = hash
		self.key = self.create_unique_key()

	def get_filename(self):
		return self.key + '.SC2Replay'
	
	def create_unique_key(self):
		existing = self.query.filter_by(hash=self.hash).first()
		if existing:
			return existing.key

		length = 6
		key = self.hash[0:length]
		while self.query.filter_by(key=key).count() > 0:
			length += 1
			if length > 40:
				break;
			key = self.hash[0:length]
		return key
	
	def upload(self, file):
		s3 = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
		bucket = s3.get_bucket(settings.S3_BUCKET)
		s3_file = boto.s3.key.Key(bucket)
		s3_file.key = self.get_filename()
		s3_file.set_contents_from_file(file)
		self.filepath = s3_file.key
