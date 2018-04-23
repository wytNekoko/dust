from flask import Blueprint, jsonify
from flask.views import MethodView
from sqlalchemy import desc

from ..models.monthly_focus import TopOwners, TopBuilders, TopPlanets
from ..logics.liquidation import liquidate

bp = Blueprint('rank', __name__, url_prefix='/rank')


class PlanetsRankView(MethodView):
    def get(self):
        plist = TopPlanets.query.limit(10)
        ret = list()
        for p in plist:
            ret.append({'name': p.pname, 'dust': p.pdust})
        return jsonify(ret)


class BuildersRankView(MethodView):
    def get(self):
        blist = TopBuilders.query.limit(10)
        ret = list()
        for b in blist:
            ret.append({'name': b.bname, 'reward_dust': b.bdust})
        return jsonify(ret)


class OwnersRankView(MethodView):
    def get(self):
        olist = TopOwners.query.limit(10)
        ret = list()
        for o in olist:
            ret.append({'name': o.oname, 'planet_dust_sum': o.odust})
        return jsonify(ret)


bp.add_url_rule('/builders', view_func=BuildersRankView.as_view('rank_builders'))
bp.add_url_rule('/planets', view_func=PlanetsRankView.as_view('rank_planets'))
bp.add_url_rule('/owners', view_func=OwnersRankView.as_view('rank_owners'))
