from datetime import datetime, time
from flask import Blueprint, jsonify, request
from flask.views import MethodView


from ..models.user_planet import *
from ..forms.planet import BuildPlanetForm, SetupPlanetForm
from ..forms.bounty import *
from ..forms.upload import *
from ..core import current_user, db, redis_store
from ..exceptions import FormValidationError, NoData, NoDust, NoTeam
from ..constants import Notify, NotifyContent
from ..helpers import register_api

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
                    current_user.owned_dust += 10
                    db.session.commit()
                    return jsonify(current_user.owned_dust)
                elif not int(t.get('tag')) == i:
                    redis_store.delete(current_user.id)
                    redis_store.hmset(current_user.id, dict(tag=i))
                    redis_store.expire(current_user.id, expire)
                    current_user.owned_dust += 10
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
            if current_user.owned_dust <= 100:
                raise NoDust()
            current_user.owned_dust -= 100
            n = Notification(type=Notify.SPY, uid=current_user.id)
            n.content = NotifyContent.get(Notify.SPY).format(p.name, p.email)
            db.session.add(n)
            db.session.commit()
            return jsonify(p.email)
        else:
            raise NoData()


class SetupBountyView(MethodView):
    def post(self):
        form = SetupBountyRewardForm()
        if form.validate():
            p = form.setup()
            return p.todict()
        else:
            raise FormValidationError(form)


class FollowView(MethodView):
    def post(self):
        n = request.get_json().get('name')
        other = User.query.filter_by(username=n)
        current_user.follow(other)
        db.session.commit()
        return jsonify('follow success')

    def delete(self, item_id):
        other = User.query.get(item_id)
        current_user.unfollow(other)
        db.session.commit()
        return jsonify('unfollow success')


class UploadProject(MethodView):
    def post(self):
        form = ProjectForm()
        if form.validate():
            p = form.create()
            return p.todict()
        else:
            raise FormValidationError(form)


class SetProject(MethodView):
    def post(self):
        form = ProjectForm()
        if form.validate():
            t = Team.query.get(current_user.cteam_id)
            p = form.set(t.project.id)
            return p.todict()
        else:
            raise FormValidationError(form)


class UploadInfo(MethodView):
    def post(self):
        form = AttenderForm()
        if form.validate():
            u = form.save()
            return u.todict()
        else:
            raise FormValidationError(form)


class CheckTeam(MethodView):
    def get(self):
        ret = dict()
        if current_user.cteam_id == 0:
            ret['inTeam'] = False
            ret['isLeader'] = False
            return ret
        ret['inTeam'] = True
        tt = Team.query.get(current_user.cteam_id)
        if tt.captain_id == current_user.id:
            ret['isLeader'] = True
        else:
            ret['isLeader'] = False
        return ret


class TeamView(MethodView):
    def post(self):
        n = request.get_json().get('name')
        if not current_user:
            raise NoData()
        t = Team(name=n, captain_id=current_user.id, competition_id=1)
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


class LikeTrue(MethodView):
    def get(self):
        true = Activity.get(1)
        true.like += 1
        return jsonify(true.like)


register_api(bp, FollowView, 'follow', '/follow')
bp.add_url_rule('/planet', view_func=SetupPlanetView.as_view('setup_planet'))
bp.add_url_rule('/get-dust', view_func=GetDustView.as_view('get_dust'))
bp.add_url_rule('/build', view_func=BuildPlanetView.as_view('build'))
bp.add_url_rule('/spy/<string:planet_name>', view_func=SpyView.as_view('spy'))
bp.add_url_rule('/bounty', view_func=SetupBountyView.as_view('setup_bounty'))
bp.add_url_rule('/up-project', view_func=UploadProject.as_view('upload_project'))
bp.add_url_rule('/set-project', view_func=SetProject.as_view('set_project'))
bp.add_url_rule('/upload-info', view_func=UploadInfo.as_view('upload_info'))
bp.add_url_rule('/check-team', view_func=CheckTeam.as_view('check_team'))
bp.add_url_rule('/true', view_func=LikeTrue.as_view('like_true'))
bp.add_url_rule('/team-manage', view_func=TeamView.as_view('team_manage'))
bp.add_url_rule('/team-add-member', view_func=AddMember.as_view('team_add_member'))
bp.add_url_rule('/team-leave', view_func=LeaveTeam.as_view('team_leave'))