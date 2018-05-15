import ast

from flask import Blueprint, request, jsonify
from flask.views import MethodView
from ..core import db, logger, oauth_client
from ..forms.register import UserRegisterForm
from ..exceptions import FormValidationError
from ..models import User


bp = Blueprint('register', __name__)


class RegisterView(MethodView):
    def post(self):
        form = UserRegisterForm()
        if form.validate():
            user = form.save()
            return user.todict()
        else:
            raise FormValidationError(form)


class RegisterAuthGithub(MethodView):
    def post(self):
        content = request.get_data()
        y = content.decode("utf-8")
        x = ast.literal_eval(y)
        code = x['code']
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
        db.session.commit()


bp.add_url_rule('/register', view_func=RegisterView.as_view('user_register'))
bp.add_url_rule('/auth/github', view_func=RegisterAuthGithub.as_view('auth_github'))
