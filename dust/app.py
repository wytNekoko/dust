import os
from flask import _request_ctx_stack, jsonify, request
from flask_migrate import Migrate

from .core import db, logger, redis_store, oauth_client#, oss
from .models.user_planet import User
from .helpers import CustomFlask, register_blueprints
from .exceptions import CustomException, FormValidationError, APITokenError, LoginRequired
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO


def create_app(config=None):
    if config is None:
        config = os.environ.get('DUST_CONFIG', 'dust.config.DevConfig')
    app = CustomFlask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    Migrate(app, db)
    redis_store.init_app(app)
    oauth_client.init_app(app)
    CORS(app, supports_credentials=True)  # 设置参数
    #chat
    SocketIO.init_app(app=app)
    # oss.init_app(app)

    before_request(app)
    register_blueprints(app, __name__.split('.', 1)[0] + '.views')
    configure_error_handles(app)

    return app


def before_request(app):
    @app.before_request
    def request_auth():
        logger.debug('### before request - blueprint: %s, endpoint: %s, method: %s, view_args: %s',
                     request.blueprint, request.endpoint, request.method, request.view_args)
        # 忽略不需要登录的blueprint
        if request.blueprint in {'login', 'register', 'rank', 'planets', 'bounty', 'hacker', 'team'}:
            return
        # 内部使用的API鉴权
        if request.blueprint in {'permission_api'}:
            if request.headers.get('X-API-Token') == 'PwO6QE4ygX':
                return
            else:
                raise APITokenError
        # 从请求中获取login_token
        auth_token = request.headers.get('X-Auth-Token')
        #auth_token = request.cookies
        if not auth_token:
            logger.debug('no auth_token')
            raise LoginRequired

        cache_data = redis_store.hgetall(auth_token)
        uid = int(cache_data.get('id', '0'))
        if not uid:
            logger.debug('auth: cache no id, %s', cache_data)
            raise LoginRequired

        user = User.query.get(uid)
        if not user:  # or user.password != cache_data['password']:
            raise LoginRequired

        # 设置user
        ctx = _request_ctx_stack.top
        ctx.user = user


def configure_error_handles(app):
    @app.errorhandler(CustomException)
    def custom_exception_handler(e):
        return jsonify(errcode=e.errcode, errmsg=e.errmsg, **e.kw)

    @app.errorhandler(FormValidationError)
    def form_validation_err_handler(e):
        return jsonify(errcode=e.errcode, errmsg=e.errmsg, errors=e.errors, **e.kw)

    @app.errorhandler(404)
    @app.errorhandler(405)
    def http_exception_handler(e):
        return jsonify(errcode=e.code, errmsg=e.name), e.code

