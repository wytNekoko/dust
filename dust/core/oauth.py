import requests, json
from ..config import DevConfig as cfg
import logging


logger = logging.getLogger(__name__)

class OAUTHException(Exception):
    # -1 conn err, -2 conn/status err -3 json err, -4 login, -5 resp.code err
    def __init__(self, code=0, msg='ok', errmsg=''):
        self.code = code
        self.msg = msg
        self.errmsg = errmsg
        logger.debug('{}-{}-{}'.format(code, msg, errmsg))
        super().__init__()


class OAUTHLoginRequired(OAUTHException):
    def __init__(self, code=-4, msg='login required', errmsg=''):
        self.code = code
        self.msg = msg
        super().__init__(code, msg, errmsg)


class OAUTHRespCodeErr(OAUTHException):
    # 除登录外的其他 resp.code 问题
    def __init__(self, code=-5, msg='resp.data.code err', errmsg=''):

        super().__init__(code, msg, errmsg)


class OAuthApi:
    OAUTH_ERR_MSG = 'OAuth error'

    def __init__(self):
        self.app = None
        self.base_url = None
        self.token_name = 'access_token'
        self.token = ''
        self.session = requests.Session()

    def init_app(self, app):
        self.app = app
        self.base_url = 'https://' # app.config['OAUTH_BACKEND_URL']

    def req(self, path, json_data, method='POST', data=None, files=None, headers=None, session=None):
        url = self.base_url + path
        session = session if session else self.session
        try:
            resp = session.request(method, url, json=json_data, data=data, files=files, headers=headers, timeout=30)
        except (requests.ConnectTimeout, requests.ReadTimeout) as e:
            raise OAUTHException(code=-1,
                                    msg='req timeout, path: {}, err:{}'.format(path, e),
                                    errmsg=self.OAUTH_ERR_MSG)
        except requests.ConnectionError as e:
            logger.error('connect to OAUTH err, err:{}'.format(e))
            raise OAUTHException(code=-2,
                                    msg='resp conn err, path:{}'.format(path),
                                    errmsg=self.OAUTH_ERR_MSG)

        if resp.status_code != 200:
            raise OAUTHException(code=-2,
                                    msg='resp status code err, path:{}:{}'.format(path, resp.status_code),
                                    errmsg=self.OAUTH_ERR_MSG)
        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise OAUTHException(code=-3,
                                    msg='resp json err, path:{}, resp:{}'.format(path, resp.text),
                                    errmsg=self.OAUTH_ERR_MSG)

        logger.debug('url: {}, resp_data:{}'.format(url, data))
        errcode = data.get('code')
        if errcode == 0:
            return data.get('data')
        elif errcode in [1003, 1001]:
            raise OAUTHLoginRequired(msg='{}'.format(data), errmsg=self.OAUTH_ERR_MSG)
        else:
            raise OAUTHRespCodeErr(code=-5,
                                      msg='errcode:{}, msg:{}'.format(errcode, data.get('msg', '')),
                                      errmsg=data.get('msg', ''))

    def set_token(self, token):
        self.token = token
        self.session.headers[self.token_name] = token

    def get_token(self, code):
        path = 'github.com/login/oauth/access_token'
        # session = requests.Session()
        data = dict(code=code, client_id=cfg['GH_CLIENT_ID'], client_secret=cfg['GH_CLIENT_SECRET'])
        header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        return self.req(path, json_data=data, method='POST', headers=header)# , session=session)

    def api(self):
        basePath = 'api.github.com/user?access_token='
        path = basePath + self.token
        return self.req(path, method='GET', headers={'Accept': 'application/json'})