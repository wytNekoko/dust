class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@127.0.0.1/dora_dust'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@127.0.0.1/dust'
    SQLALCHEMY_ECHO = True
    REDIS_URL = "redis://localhost:6379/0"
    LOGIN_EXPIRE_TIME = 7200*12


class DevConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False
    REDIS_URL = "redis://localhost:6379/1"


class PrdConfig(Config):
    REDIS_URL = "redis://localhost:6379/2"

