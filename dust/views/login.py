import binascii
import os
from datetime import datetime

from flask import Blueprint, current_app, request
from flask.views import MethodView

from ..core import redis_store
from ..exceptions import LoginInfoError, LoginInfoRequired, NoError
from ..models.user_planet import User

bp = Blueprint('login', __name__)


class LoginView(MethodView):
    def post(self):
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        if not (username and password):
            raise LoginInfoRequired

        user = User.get_by_username(username)
        if not (user and user.check_password(password)):
            raise LoginInfoError
        auth_token = binascii.hexlify(os.urandom(16)).decode()  # noqa
        redis_store.hmset(auth_token, dict(
            id=user.id,
            password=user.password,
            created_at=datetime.now()
        ))
        expires_in = current_app.config.get('LOGIN_EXPIRE_TIME', 7200)
        redis_store.expire(auth_token, expires_in)

        return dict(auth_token=auth_token, expires_in=expires_in, id=user.id)


class LogoutView(MethodView):
    def get(self):
        auth_token = request.headers.get('X-Auth-Token')
        if auth_token:
            redis_store.delete(auth_token)
        raise NoError


bp.add_url_rule('/login', view_func=LoginView.as_view('login'))
bp.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
