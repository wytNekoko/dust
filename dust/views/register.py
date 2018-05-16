import ast
import binascii
import datetime
import os
from flask import Blueprint, current_app, request
from flask.views import MethodView
from ..core import db, logger, oauth_client, redis_store
from ..forms.register import UserRegisterForm
from ..exceptions import FormValidationError
from ..models.user_planet import User, Notification
from ..constants import Notify, NotifyContent

bp = Blueprint('register', __name__)


class RegisterView(MethodView):
    def post(self):
        form = UserRegisterForm()
        if form.validate():
            user = form.save()
            return user.todict()
        else:
            raise FormValidationError(form)


class AuthGithub(MethodView):
    def get(self):
        content = request.get_data()
        y = content.decode("utf-8")
        x = ast.literal_eval(y)
        code = x['code']
        return {'code': code}


class RegisterAuthGithub(MethodView):
    def post(self):
        code = request.get_json().get('code')
        resp = oauth_client.get_token(code)
        logger.debug('### oauth_client resp', resp)
        logger.debug('### oauth_client resp.data', resp.data)
        logger.debug('### oauth_client resp.json', resp.json)
        access_token = resp.json.get('access_token')
        oauth_client.set_token(access_token)
        user_info = oauth_client.api()
        logger.debug('### github user', user_info)
        u = User(username=user_info.get('login'))
        u.git_account = user_info.get('email')
        u.github_link = user_info.get('html_url')
        db.session.add(u)
        db.session.flush()
        auth_token = binascii.hexlify(os.urandom(16)).decode()  # noqa
        redis_store.hmset(auth_token, dict(
            id=u.id,
            created_at=datetime.now(),
        ))
        n = Notification(type=Notify.BUILD, uid=u.id)
        db.session.add(n)
        expires_in = current_app.config.get('LOGIN_EXPIRE_TIME', 7200*12)  # expire in 1 day
        redis_store.expire(auth_token, expires_in)
        redis_store.set("%s:build_times" % u.id, 3, ex=expires_in)
        n.content = NotifyContent.get(Notify.BUILD).format('3')
        db.session.commit()
        return dict(auth_token=auth_token, expires_in=expires_in, user_info=u.todict())


bp.add_url_rule('/register', view_func=RegisterView.as_view('user_register'))
bp.add_url_rule('/auth/github', view_func=AuthGithub.as_view('auth_github'))
bp.add_url_rule('/register/github', view_func=RegisterAuthGithub.as_view('register_github'))
