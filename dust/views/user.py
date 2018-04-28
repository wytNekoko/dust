from datetime import datetime, time
from flask import Blueprint, jsonify, request
from flask.views import MethodView

from ..models.user_planet import User, Planet, Suggestion
from ..forms.planet import BuildPlanetForm, SetupPlanetForm
from ..core import current_user, db, redis_store
from ..exceptions import FormValidationError, NoData

bp = Blueprint('user', __name__, url_prefix='/user')

time_end = [0, 8, 16, 24]


class GetDustView(MethodView):
    """get dust from system every day"""
    def post(self):
        now = datetime.now()
        expire = 3600*8
        for i in range(3):
            if time_end[i] <= now.hour < time_end[i+1]:
                t = redis_store.hgetall(current_user.id)
                if not t:
                    redis_store.hmset(current_user.id, dict(tag=i))
                    redis_store.expire(current_user.id, expire)
                    current_user.owned_dust += 88
                    db.session.commit()
                    return jsonify(current_user.owned_dust)
                elif not int(t.get('tag')) == i:
                    redis_store.delete(current_user.id)
                    redis_store.hmset(current_user.id, dict(tag=i))
                    redis_store.expire(current_user.id, expire)
                    current_user.owned_dust += 88
                    db.session.commit()
                    return jsonify(current_user.owned_dust)
                else:
                    delta = time_end[i+1] - now.hour
                    if delta == 1:
                        return jsonify('You can get it again in 1 hour')
                    elif delta == 0:
                        return jsonify('You can get it again in 8 hours')
                    else:
                        return jsonify('You can get it again in %d hours' % delta)


class SetupPlanetView(MethodView):
    # def get(self):
    #     planets = Planet.query.all()
    #     return jsonify(planets)

    def post(self):
        form = SetupPlanetForm()
        if form.validate():
            p = form.setup()
            return p.todict()
        else:
            raise FormValidationError(form)


class BuildPlanetView(MethodView):
    def post(self):
        form = BuildPlanetForm()
        if form.validate():
            record = form.build()
            return record.todict()
        else:
            raise FormValidationError(form)


class SpyView(MethodView):
    def get(self, planet_name=None):
        if planet_name:
            p = Planet.query.filter_by(name=planet_name).first()
        else:
            name = request.get_json().get('planet_name', '')
            p = Planet.query.filter_by(name=name).first()
        if p:
            current_user.owned_dust -= 1000
            # owner = User.query.get(p.owner_id)
            # owner.owned_dust += 1000
            db.session.commit()
            return jsonify(p.email)
        else:
            raise NoData()


class SuggestView(MethodView):
    def post(self):
        content = request.get_json().get('content', '')
        new_sug = Suggestion(uid=current_user.id, content=content)
        db.session.add(new_sug)
        db.session.commit()
        return jsonify()


bp.add_url_rule('/planet', view_func=SetupPlanetView.as_view('setup_planet'))
bp.add_url_rule('/get-dust', view_func=GetDustView.as_view('get_dust'))
bp.add_url_rule('/build', view_func=BuildPlanetView.as_view('build'))
bp.add_url_rule('/spy/<string:planet_name>', view_func=SpyView.as_view('spy'))
bp.add_url_rule('/suggest', view_func=SuggestView.as_view('suggest'))
