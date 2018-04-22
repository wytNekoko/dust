import oss2
from mimetypes import guess_extension
import uuid


class FlaskOSS:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        endpoint = app.config['OSS_ENDPOINT']
        access_key_id = app.config['OSS_ACCESS_KEY_ID']
        access_key_secret = app.config['OSS_ACCESS_KEY_SECRET']
        default_bucket_name = app.config['OSS_DEFAULT_BUCKET_NAME']
        self.domain_schema = app.config.get('OSS_DOMAIN_SCHEMA', 'http')
        self.domain = app.config['OSS_DOMAIN']

        self.endpoint = endpoint
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = self.get_bucket(default_bucket_name)

    def get_bucket(self, bucket_name):
        # 使用非默认bucket使用这个方法创建bucket
        return oss2.Bucket(self.auth, self.endpoint, bucket_name)


def gen_filename(mimetype=''):
    """使用uuid生成随机文件名
    :params mimetype: 用于生成文件扩展名
    """
    ext = guess_extension(mimetype)
    if ext == '.jpe':
        ext = '.jpg'
    return uuid.uuid4().hex + ext
