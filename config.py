import os

class Config(object):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:data_scientist@db/route_client'
	SECRET_KEY = os.urandom(32)
	SESSION_TYPE = 'filesystem'