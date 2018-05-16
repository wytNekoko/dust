from flask import Blueprint, jsonify, request
from flask.views import MethodView

from ..models.user_planet import BuildRecord, Planet
from ..core import current_user, db
from ..exceptions import FormValidationError, NoData

bp = Blueprint('profile', __name__, url_prefix='/profile')


class OwnedPlanets(MethodView):
    def get(self):
        ps = current_user.owned_planets
        return jsonify([{'name': p.name, 'description': p.description, 'dust_num': p.dust_num} for p in ps])


class BuildedPlanets(MethodView):
    def get(self):
        rd = BuildRecord.query.filter_by(builder_id=current_user.id).all()
        ret = list()
        planets = dict()
        for r in rd:
            p = Planet.query.get(r.planet_id)
            if planets.get(p.name):
                planets[p.name] += r.reward
            else:
                planets[p.name] = r.reward

        for k, v in planets.items():
            p = Planet.query.filter_by(name=k).first()
            ret.append(dict(name=k, description=p.description, reward_dust=v))
        return jsonify(ret)


class MainProfile(MethodView):
    def get(self):
        ret = dict()
        ret['total_dust'] = current_user.owned_dust
        ret['github_link'] = current_user.github_link
        # ps = current_user.owned_planets
        # ret['planets'] = [{'created_at': p.created_at, 'name': p.name, 'reward': p.reward} for p in ps]
        return jsonify(ret)


class PostedRewards(MethodView):
    def get(self):
        pr = current_user.bounty_rewards
        return jsonify([{'name': p.name, 'description': p.description} for p in pr])


bp.add_url_rule('/owned-planets', view_func=OwnedPlanets.as_view('owned_planets'))
bp.add_url_rule('/builded-planets', view_func=BuildedPlanets.as_view('builded_planets'))
bp.add_url_rule('/main', view_func=MainProfile.as_view('main_profile'))