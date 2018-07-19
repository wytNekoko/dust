class Config(object):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@127.0.0.1/dust'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Dorahacks@127.0.0.1/dust'
    SQLALCHEMY_ECHO = True
    REDIS_URL = "redis://localhost:6379/0"
    LOGIN_EXPIRE_TIME = 7200*12
    GH_CLIENT_ID = 'ae68a17db805afccb892'
    GH_CLIENT_SECRET = 'a375812e01297db4f39d48b65dbb324633e70b7d'
    OSS_ENDPOINT = 'oss-us-west-1-internal.aliyuncs.com'
    OSS_ACCESS_KEY_ID = 'LTAIundQqyZr7vYP'
    OSS_ACCESS_KEY_SECRET = '7ETdRwgIRHjF7DU1uOMJsxd6IODRed'
    OSS_DEFAULT_BUCKET_NAME = 'dorahacks-fund'
    OSS_DOMAIN_SCHEMA = 'https'
    OSS_DOMAIN = 'oss-us-west-1.aliyuncs.com'


class DevConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False
    REDIS_URL = "redis://localhost:6379/1"


class PrdConfig(Config):
    REDIS_URL = "redis://localhost:6379/2"

