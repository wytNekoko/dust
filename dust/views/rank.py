from flask import Blueprint, jsonify
from flask.views import MethodView
from sqlalchemy import desc

from ..models.user_planet import User
from ..logics.liquidation import liquidate

bp = Blueprint('rank', __name__, url_prefix='/rank')


class PlanetsRankView(MethodView):
    def get(self):
        plist = liquidate()
        return jsonify(plist)


class BuildersRankView(MethodView):
    def get(self):
        ulist = User.query.order_by(desc(User.build_reward_dust)).limit(10)
        return jsonify(ulist)


class OwnersRankView(MethodView):
    def get(self):
        ulist = User.query.order_by(desc(User.planet_dust_sum)).limit(10)
        return jsonify(ulist)


bp.add_url_rule('/builders', view_func=BuildersRankView.as_view('rank_builders'))
bp.add_url_rule('/planets', view_func=PlanetsRankView.as_view('rank_planets'))
bp.add_url_rule('/owners', view_func=OwnersRankView.as_view('rank_owners'))
