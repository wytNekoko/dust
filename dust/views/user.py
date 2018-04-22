from flask import Blueprint, jsonify, request
from flask.views import MethodView

from ..models.user_planet import User, Planet, Suggestion
from ..forms.planet import BuildPlanetForm, SetupPlanetForm
from ..core import current_user, db
from ..exceptions import FormValidationError, exceptions

bp = Blueprint('user', __name__, url_prefix='/user')


class GetDustView(MethodView):
    """get dust from system every day"""
    def get(self):
        """TODO: how many times left in a day"""
        return jsonify()

    def post(self):
        current_user.owned_dust += 88
        db.session.commit()
        return jsonify(current_user.owned_dust)


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
    def get(self, planet_name):
        # planet_name = request.get_json().get('name', '')
        if planet_name:
            p = Planet.query.filter_by(name=planet_name).first()
            if p:
                current_user.owned_dust -= 1000
                owner = User.query.get(p.owner_id)
                owner.owned_dust += 1000
                db.session.commit()
                return jsonify(p.email)
        return exceptions.NoData


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
bp.add_url_rule('/spy', view_func=SpyView.as_view('spy'))
