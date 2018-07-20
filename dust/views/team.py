from flask import Blueprint, jsonify, request
from flask.views import MethodView

from ..models.user_planet import *
from ..core import current_user, db, redis_store
from ..exceptions import FormValidationError, NoTeam, NoData

bp = Blueprint('team', __name__, url_prefix='/team')


class TeamView(MethodView):
    def post(self):
        n = request.get_json().get('name')
        if not current_user:
            raise NoData()
        t = Team(name=n, captain_id=current_user.id)
        db.session.add(t)
        db.session.flush()
        u = User.query.get(current_user.id)
        u.cteam_id = t.id
        db.session.commit()
        return t

    def put(self):
        if current_user.cteam_id == 0:
            raise NoTeam()
        item = Team.query.get(current_user.cteam_id)
        item.is_completed = True
        db.session.commit()
        return jsonify('team completed')

    def delete(self):
        item = Team.query.get(current_user.cteam_id)
        item.delete()
        return jsonify('team dismiss')


class AddMember(MethodView):
    def post(self):
        n = request.get_json().get('member_id')
        if current_user.cteam_id == 0:
            raise NoTeam()
        if not n:
            raise NoData()
        t = Team.query.get(current_user.cteam_id)
        u = User.query.get(n)
        u.cteam_id = t.id
        t.users.append(u)
        db.session.commit()
        return t.todict()


class LeaveTeam(MethodView):
    def post(self):
        if current_user.cteam_id == 0:
            raise NoTeam()
        t = Team.query.get(current_user.cteam_id)
        t.users.remove(current_user)
        db.session.commit()
        return t.users


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
            members = [dict(username=u.username, role=u.role, avatar=u.avatar)for u in t.users]
            tmp = dict(name=t.name, members=members)
            res.append(tmp)
        return jsonify(res)


class Attender(MethodView):
    def get(self, role):
        us = User.query.filter_by(role=role)

        if us:
            return jsonify([dict(url=u.avatar, name=u.hacker_name, intro=u.slogan, uid=u.id) for u in us])
        else:
            raise NoData()


bp.add_url_rule('/manage', view_func=TeamView.as_view('team_manage'))
bp.add_url_rule('/add-member', view_func=AddMember.as_view('team_add_member'))
bp.add_url_rule('/leave', view_func=LeaveTeam.as_view('team_leave'))
bp.add_url_rule('/<string:team_id>', view_func=TeamDetail.as_view('team_detail'))
bp.add_url_rule('/list/<int:status>', view_func=TeamList.as_view('team_list'))
bp.add_url_rule('/attenders/<string:role>', view_func=Attender.as_view('attender'))
