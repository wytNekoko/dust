import binascii
import os
from datetime import datetime
from flask import Blueprint, current_app, request
from flask.views import MethodView

from ..core import redis_store,  db, oauth_client
from ..exceptions import LoginInfoError, LoginInfoRequired, NoError, LoginAuthError, RegisterFailError
from ..models.user_planet import User, Notification
from ..constants import Notify, NotifyContent

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
            created_at=datetime.now(),
        ))
        expires_in = current_app.config.get('LOGIN_EXPIRE_TIME', 7200*12)  # expire in 1 day
        redis_store.expire(auth_token, expires_in)

        # s = redis_store.get("%s:build_times" % user.id)
        # if not s:
        #     n = Notification(type=Notify.BUILD, uid=user.id)
        #     db.session.add(n)
        #     redis_store.set("%s:build_times" % user.id, 3, ex=expires_in)
        #     n.content = NotifyContent.get(Notify.BUILD).format('3')
        # db.session.commit()

        return dict(auth_token=auth_token, expires_in=expires_in, user_info=user.todict())


class LogoutView(MethodView):
    def get(self):
        auth_token = request.headers.get('X-Auth-Token')
        if auth_token:
            redis_store.delete(auth_token)
        raise NoError


class LoginAuthGithub(MethodView):
    def post(self):
        code = request.get_json().get('code')
        resp = oauth_client.get_token(code)
        access_token = resp.json().get('access_token')
        if not access_token:
            raise LoginAuthError()
        oauth_client.set_token(access_token)
        user_info = oauth_client.user().json()
        u1 = User.get_by_username(user_info.get('login'))
        u2 = User.query.filter_by(git_account=user_info.get('login')).first()
        if not u1 and not u2:
            u = User(username=user_info.get('login'))
            u.git_account = user_info.get('login')
            u.github_link = user_info.get('html_url')
            u.avatar = user_info.get('avatar_url')
            db.session.add(u)
            db.session.flush()
            db.session.commit()
        elif u1 and not u2:
            u = u1
        elif u2 and not u1:
            u = u2
        elif u1 == u2:
            u = u1
            # raise RegisterFailError()
        auth_token = binascii.hexlify(os.urandom(16)).decode()  # noqa
        redis_store.hmset(auth_token, dict(
            id=u.id,
            created_at=datetime.now(),
        ))
        expires_in = current_app.config.get('LOGIN_EXPIRE_TIME', 7200*12)  # expire in 1 day
        redis_store.expire(auth_token, expires_in)

        # s = redis_store.get("%s:build_times" % user.id)
        # if not s:
        #     n = Notification(type=Notify.BUILD, uid=user.id)
        #     db.session.add(n)
        #     redis_store.set("%s:build_times" % user.id, 3, ex=expires_in)
        #     n.content = NotifyContent.get(Notify.BUILD).format('3')
        # db.session.commit()

        return dict(auth_token=auth_token, expires_in=expires_in, user_info=u.todict())


bp.add_url_rule('/login', view_func=LoginView.as_view('login'))
bp.add_url_rule('/auth-login/github', view_func=LoginAuthGithub.as_view('login_github'))
bp.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
