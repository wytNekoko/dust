from flask import Blueprint, jsonify, request
from flask.views import MethodView
from sqlalchemy import desc
from ..helpers import *
from ..models.user_planet import *
from ..models.monthly_focus import TopOwners, TopBuilders, TopPlanets

bp = Blueprint('rank', __name__, url_prefix='/rank')


class DashboardView(MethodView):
    def get(self):
        ret = dict()
        ps = Planet.query.order_by(desc(Planet.dust_num)).limit(10)
        ret['planets'] = [{'name': p.name, 'dust': p.dust_num} for p in ps]
        os = User.query.order_by(desc(User.planet_dust_sum)).limit(10)
        ret['owners'] = [{'username': o.username, 'dust': o.planet_dust_sum} for o in os]
        bs = User.query.order_by(desc(User.build_reward_dust)).limit(10)
        ret['builders'] = [{'username': b.username, 'dust': b.build_reward_dust} for b in bs]
        return jsonify(ret)


class WinnerView(MethodView):
    def get(self):
        ret = dict()
        ps = TopPlanets.query.limit(10)
        ret['planets'] = [{'name': p.pname, 'dust': p.pdust} for p in ps]
        os = TopOwners.query.limit(10)
        ret['owners'] = [{'username': o.oname, 'dust': o.odust} for o in os]
        bs = TopBuilders.query.limit(10)
        ret['builders'] = [{'username': b.bname, 'dust': b.bdust} for b in bs]
        return jsonify(ret)


class BountyView(MethodView):
    def get(self):
        ret = dict()
        rs = BountyReward.query.order_by(BountyReward.reward.desc()).limit(10)
        ret['rewards'] = [{'name': r.name, 'dust': r.reward} for r in rs]
        ret['hunters'] = []
        return jsonify(ret)


class HackerView(MethodView):
    def get(self):
        ret = list()
        hs = User.query.order_by(User.planet_dust_sum.desc())
        for h in hs:
            x = dict(hacker=h.username, project_num=len(h.owned_planets), gift=h.planet_dust_sum)
            ret.append(x)
        return jsonify(ret)


class ProjectView(MethodView):
    def post(self):
        req_data = request.get_json()
        page = req_data.get('page')
        per_page = req_data.get('per_page')
        ts = Team.query.filter_by(is_active=True).order_by(Team.ballot.desc()).paginate(page, per_page=per_page, error_out=False)
        res = {
            'items': [],
            'page': page if page else 1,
            'pages': 1 if ts.total / per_page <= 1 else int(ts.total / per_page) + 1,
            'total': ts.total,
            'per_page': per_page
        }
        for t in ts.items:
            p = Project.query.filter_by(team_id=t.id).first()
            if p:
                info = p.todict()
                info['team'] = t.todict()
                info['received'] = True
                res['items'].append(info)
        return jsonify(res)


class NknContributorsView(MethodView):
    def get(self):
        records = ContributeRecord.query.filter_by(chain_name='NKN').order_by(ContributeRecord.author_id.desc()).all()
        tmp = list()
        for r in records:
            if not tmp:
                t = r.todict()
                t['github'] = 'https://github.com' + r.author_login
                tmp.append(t)
                continue
            if tmp[-1].author_id == r.author_id:
                tmp[-1].commit += r.commit
            else:
                t = r.todict()
                t['github'] = 'https://github.com' + r.author_login
                tmp.append(t)
        tmp.sort(reverse=True, key=sort_dict_commit())
        return jsonify(tmp)


bp.add_url_rule('/dashboard', view_func=DashboardView.as_view('rank_dashboard'))
bp.add_url_rule('/winners', view_func=WinnerView.as_view('rank_winners'))
bp.add_url_rule('/bounty', view_func=BountyView.as_view('rank_bounty'))
bp.add_url_rule('/hacker', view_func=HackerView.as_view('rank_hackers'))
bp.add_url_rule('/project', view_func=ProjectView.as_view('rank_projects'))
bp.add_url_rule('/nkn/contributors', view_func=NknContributorsView.as_view('NKN_contributors'))