from flask import Blueprint, jsonify, request
from flask.views import MethodView
from sqlalchemy import func

from ..core import redis_store, logger
from ..models.user_planet import *
from ..exceptions import NoData, CacheTokenError
from ..constants import Status

bp = Blueprint('planets', __name__, url_prefix='/planets')


class ShowcaseView(MethodView):
    def get(self):
        plist = Planet.query.filter_by(status=Status.DEFAULT).order_by(func.rand()).limit(16)
        ret = list()
        for i in range(plist.count()):
            ret.append({'name': plist[i].name,
                        'description': plist[i].description,
                        'demo': plist[i].demo_url,
                        'git': plist[i].github_url,
                        'team': plist[i].team_intro,
                        'created_at': plist[i].created_at
                        })
        return jsonify(ret)


class GetOnePlanetView(MethodView):
    def get(self, planet_name):
        p = Planet.query.filter_by(name=planet_name).first()
        if p:
            x = p.todict()
            x['created_at'] = p.created_at
            return x
        else:
            raise NoData()


class AllPlanetsView(MethodView):
    def get(self):
        planets = Planet.query.filter_by(status=Status.DEFAULT)  # can't be .all(), which returns a list
        ps = planets.paginate()
        records = list()
        for p in ps.items:
            tmp = p.todict()
            tmp['created_at'] = p.created_at
            records.append(tmp)
        #records = [p.todict() for p in ps.items]
        return jsonify(
            records=records,
            total=ps.total,
            page=ps.page,
            per_page=ps.per_page,
            pages=ps.pages
        )


class RankListView(MethodView):
    def get(self):
        planets = Planet.query.filter_by(status=Status.DEFAULT).order_by(Planet.dust_num.desc())
        # ret = [p.todict() for p in planets]
        ret = list()
        for index, value in enumerate(planets):
            x = planets[index].todict()
            x['rank'] = index + 1
            ret.append(x)
        return jsonify(ret)


class ProjectView(MethodView):
    def get(self):
        ps = Project.query.all()
        ret = [p.todict() for p in ps]
        return jsonify(ret)


class DAppListView(MethodView):
    def get(self, uid):
        ds = DApp.query.order_by(DApp.vote.desc()).all()
        ret = dict()
        ret['dapps'] = [d.todict() for d in ds]
        ret['voted_dapp_id'] = 0
        if uid != 0:
            record = DAppVoteRecord.query.filter_by(from_uid=uid).first()
            if record:
                ret['voted_dapp_id'] = record.to_did
        return jsonify(ret)


class DAppView(MethodView):
    def get(self, uid):
        dapp = DApp.query.filter_by(uid=uid).all()
        if not dapp:
            raise NoData()
        ret = [d.todict() for d in dapp]
        return jsonify(ret)


bp.add_url_rule('/show', view_func=ShowcaseView.as_view('show_planets'))
bp.add_url_rule('/one/<string:planet_name>', view_func=GetOnePlanetView.as_view('one_planet'))
bp.add_url_rule('/all', view_func=AllPlanetsView.as_view('all_planets'))
bp.add_url_rule('/ranklist', view_func=RankListView.as_view('rank_list'))
bp.add_url_rule('/dapp/list/<int:uid>', view_func=DAppListView.as_view('dapp_list'))
bp.add_url_rule('/dapp/<int:uid>', view_func=DAppView.as_view('dapp'))