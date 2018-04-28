from flask import Blueprint, jsonify
from flask.views import MethodView
from sqlalchemy import func

from ..models.user_planet import Planet
from ..exceptions import NoData
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
            return p.todict()
        else:
            raise NoData()


bp.add_url_rule('/show', view_func=ShowcaseView.as_view('show_planets'))
bp.add_url_rule('/one/<string:planet_name>', view_func=GetOnePlanetView.as_view('one_planet'))
