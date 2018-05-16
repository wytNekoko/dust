class Config(object):
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@127.0.0.1/dora_dust'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@127.0.0.1/dust'
    SQLALCHEMY_ECHO = True
    REDIS_URL = "redis://localhost:6379/0"
    LOGIN_EXPIRE_TIME = 7200*12
    GH_CLIENT_ID = '153a7fb787d1bd541839'
    GH_CLIENT_SECRET = 'ca6ea91331f6b8de9620418dbe1a84f491caaa64'

class DevConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False
    REDIS_URL = "redis://localhost:6379/1"


class PrdConfig(Config):
    REDIS_URL = "redis://localhost:6379/2"

