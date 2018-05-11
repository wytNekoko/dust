from flask import Blueprint, jsonify
from flask.views import MethodView
from sqlalchemy import desc
from ..models.user_planet import Planet, User
from ..models.monthly_focus import TopOwners, TopBuilders, TopPlanets

bp = Blueprint('rank', __name__, url_prefix='/rank')


class DashboardView(MethodView):
    def get(self):
        ret = dict()
        ps = Planet.query.order_by(desc(Planet.dust_num)).limit(10)
        ret['planets'] = [{'name': p.name, 'dust': p.dust_num} for p in ps]
        os = User.query.order_by(desc(User.planet_dust_sum)).limit(10)
        ret['owners'] = [{'username': o.username, 'dust': o.planet_dust_sum} for o in os]
        bs = User.query.order_by(desc(User.build_reward_dust)).limit(10)
        ret['builders'] = [{'username': b.username, 'dust': b.build_reward_dust} for b in bs]
        return jsonify(ret)


class WinnerView(MethodView):
    def get(self):
        ret = dict()
        ps = TopPlanets.query.limit(10)
        ret['planets'] = [{'name': p.pname, 'dust': p.pdust} for p in ps]
        os = TopOwners.query.limit(10)
        ret['owners'] = [{'username': o.oname, 'dust': o.odust} for o in os]
        bs = TopBuilders.query.limit(10)
        ret['builders'] = [{'username': b.bname, 'dust': b.bdust} for b in bs]
        return jsonify(ret)


bp.add_url_rule('/dashboard', view_func=DashboardView.as_view('rank_dashboard'))
bp.add_url_rule('/winners', view_func=WinnerView.as_view('rank_winners'))