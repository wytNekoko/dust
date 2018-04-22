from flask import Blueprint, jsonify
from flask.views import MethodView
from sqlalchemy import func

from ..models.user_planet import Planet

bp = Blueprint('planets', __name__, url_prefix='/planets')


class ShowcaseView(MethodView):
    def get(self):
        plist = Planet.query.order_by(func.rand()).limit(16)
        ret = list()
        for i in range(16):
            ret.append({'name': plist[i].name,
                        'description': plist[i].description,
                        'demo': plist[i].demo_url,
                        'git': plist[i].github_url,
                        'team': plist[i].team_intro})
        return jsonify(ret)


bp.add_url_rule('/show', view_func=ShowcaseView.as_view('show_planets'))
