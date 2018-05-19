from flask import Blueprint, jsonify, request
from flask.views import MethodView
\
from ..core import current_user, db
from ..exceptions import FormValidationError, NoData

bp = Blueprint('profile', __name__, url_prefix='/profile')


class MainProfile(MethodView):
    def get(self):
        ret = dict()
        ret['total_dust'] = current_user.owned_dust
        ret['github_link'] = current_user.github_link
        # ps = current_user.owned_planets
        # ret['planets'] = [{'created_at': p.created_at, 'name': p.name, 'reward': p.reward} for p in ps]
        return jsonify(ret)


bp.add_url_rule('/main', view_func=MainProfile.as_view('main_profile'))