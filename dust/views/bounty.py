from flask import Blueprint, jsonify
from flask.views import MethodView

from ..forms.bounty import *
from ..models.user_planet import BountyReward
from ..exceptions import NoData, FormValidationError
from ..constants import Status

bp = Blueprint('bounty', __name__, url_prefix='/bounty')


class GetBountyView(MethodView):
    def get(self):
        s = BountyReward.query.all()
        return jsonify(s)


bp.add_url_rule('/show', view_func=GetBountyView.as_view('show_bounty'))
