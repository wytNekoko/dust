from flask import Blueprint, jsonify, request
from flask.views import MethodView

from ..models.user_planet import BuildRecord, Planet, User
from ..core import current_user
from ..exceptions import FormValidationError, NoData

bp = Blueprint('hacker', __name__, url_prefix='/hacker')


class OwnedPlanets(MethodView):
    def get(self, username):
        user = User.get_by_username(username)
        ps = user.owned_planets
        return jsonify([{'name': p.name, 'description': p.description, 'dust_num': p.dust_num} for p in ps])


class BuildedPlanets(MethodView):
    def get(self, username):
        user = User.get_by_username(username)
        rd = BuildRecord.query.filter_by(builder_id=user.id).all()
        if not rd:
            return jsonify()
        ret = list()
        planets = dict()
        for r in rd:
            p = Planet.query.get(r.planet_id)
            if not p:
                continue
            if planets.get(p.name):
                planets[p.name] += r.reward
            else:
                planets[p.name] = r.reward

        for k, v in planets.items():
            p = Planet.query.filter_by(name=k).first()
            ret.append(dict(name=k, description=p.description, reward_dust=v))
        return jsonify(ret)


class PostedRewards(MethodView):
    def get(self):
        pr = current_user.bounty_rewards
        return jsonify([{'name': p.name, 'description': p.description} for p in pr])


class Hacker(MethodView):
    def get(self, username):
        u = User.get_by_username(username)
        return jsonify({'name': u.username, 'property': u.owned_dust, 'projects': len(u.owned_planets)})


bp.add_url_rule('/<string:username>', view_func=Hacker.as_view('personal'))
bp.add_url_rule('/owned-planets/<string:username>', view_func=OwnedPlanets.as_view('owned_planets'))
bp.add_url_rule('/builded-planets/<string:username>', view_func=BuildedPlanets.as_view('builded_planets'))
