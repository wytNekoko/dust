from flask import Blueprint, jsonify, request
from flask.views import MethodView

from ..core import current_user, db, oauth_client
from ..exceptions import FormValidationError, NoData, EmptyUserInfo, LoginAuthError

bp = Blueprint('profile', __name__, url_prefix='/profile')


class MainProfile(MethodView):
    def get(self):
        if not current_user:
            raise EmptyUserInfo()
        ret = current_user.to_dict()
        ret['total_gift'] = current_user.owned_dust
        ret['github_link'] = current_user.github_link
        # ps = current_user.owned_planets
        # ret['planets'] = [{'created_at': p.created_at, 'name': p.name, 'reward': p.reward} for p in ps]
        return jsonify(ret)


class BindGit(MethodView):
    def post(self):
        code = request.get_json().get('code')
        resp = oauth_client.get_token(code)
        access_token = resp.json().get('access_token')
        if not access_token:
            raise LoginAuthError()
        oauth_client.set_token(access_token)
        user_info = oauth_client.user().json()
        current_user.git_account = user_info.get('login')
        current_user.github_link = user_info.get('html_url')
        db.session.commit()
        return jsonify()


bp.add_url_rule('/main', view_func=MainProfile.as_view('main_profile'))