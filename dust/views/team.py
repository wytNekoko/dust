from flask import Blueprint, jsonify, request
from flask.views import MethodView

from ..models.user_planet import *
from ..core import current_user, db, redis_store
from ..exceptions import FormValidationError, NoTeam, NoData

bp = Blueprint('team', __name__, url_prefix='/team')


class TeamDetail(MethodView):
    def get(self, team_id):
        te = Team.query.get(team_id)
        res = te.todict()
        res['teammates'] = list()
        for us in res.users:
            tmp = dict(id=us.id, avatar=us.avatar, role=us.role)
            # TODO role changes according to competitions
            res['teammates'].append(tmp)
        return te.todict()


class TeamList(MethodView):
    def get(self, status):
        if status == 0:
            ts = Team.query.filter_by(is_completed=False)
        else:
            ts = Team.query.filter_by(is_completed=True)
        res = list()
        for t in ts:
            members = [dict(username=u.username, name=u.hacker_name, role=u.role, avatar=u.avatar, uid=u.id) for u in t.users]
            tmp = dict(name=t.name, tid=t.id, members=members)
            res.append(tmp)
        return jsonify(res)


class Attender(MethodView):
    def get(self, role):
        us = User.query.filter_by(role=role, is_hacker=True)
        if us:
            return jsonify([dict(url=u.avatar, name=u.hacker_name, intro=u.slogan, uid=u.id, team_id=u.cteam_id) for u in us])
        else:
            raise NoData()


bp.add_url_rule('/<string:team_id>', view_func=TeamDetail.as_view('team_detail'))
bp.add_url_rule('/list/<int:status>', view_func=TeamList.as_view('team_list'))
bp.add_url_rule('/attenders/<string:role>', view_func=Attender.as_view('attender'))
