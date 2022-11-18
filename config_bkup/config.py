import os

class Config(object):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:datascientist@127.0.0.1/route_client'
	SECRET_KEY = os.urandom(32)
	SESSION_TYPE = 'filesystem'