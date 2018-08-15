from flask import Blueprint, jsonify, request
from flask.views import MethodView

from ..models.user_planet import *
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
    def post(self):
        hackername = request.get_json().get('name')
        cid = request.get_json().get('cid')
        if cid == 0:
            c = Contributor.query.filter_by(author_login=hackername).first()
        else:
            c = Contributor.query.get(cid)
        if not c:
            raise NoData()
        ret = c.todict()
        records = ContributeRecord.query.filter_by(author_login=c.author_login).order_by(
            ContributeRecord.commit.desc()).limit(10)
        ret['commit_info'] = [r.todict() for r in records]
        return jsonify(ret)


class GithubContribute(MethodView):
    def post(self):
        req_data = request.get_json()
        page = req_data.get('page')
        per_page = req_data.get('per_page')
        gs = Contributor.query.order_by(Contributor.score.desc()).paginate(page, per_page=per_page, error_out=False)

        res = {
            'items': [],
            'page': page if page else 1,
            'pages': 1 if gs.total / per_page <= 1 else int(gs.total / per_page) + 1,
            'total': gs.total,
            'per_page': per_page
        }
        for index, g in enumerate(gs.items):
            info = g.todict()
            commit_info = ContributeRecord.query.filter_by(author_login=g.author_login).order_by(
                ContributeRecord.commit.desc()).limit(2)
            info['rank'] = (page - 1) * 10 + index + 1
            info['commit'] = [cc.todict() for cc in commit_info]
            res['items'].append(info)
        return jsonify(res)


class SearchContributorByChainName(MethodView):
    def post(self):
        req_data = request.get_json()
        page = req_data.get('page')
        per_page = req_data.get('per_page')
        chain_name = req_data.get('chain_name')
        gss = db.session.query(ContributeRecord.author_login).filter_by(chain_name=chain_name).distinct(
            ContributeRecord.author_login).paginate(page, per_page=per_page, error_out=False)
        aa = [cc.author_login for cc in gss.items]
        gs = Contributor.query.filter(Contributor.author_login.in_(aa)).order_by(Contributor.score.desc()).paginate(
            page, per_page=per_page, error_out=False)
        res = {
            'items': [],
            'page': page if page else 1,
            'pages': 1 if gs.total / per_page <= 1 else int(gs.total / per_page) + 1,
            'total': gs.total,
            'per_page': per_page
        }

        for index, g in enumerate(gs.items):
            info = g.todict()
            commit_info = ContributeRecord.query.filter_by(author_login=g.author_login, chain_name=chain_name).order_by(
                ContributeRecord.commit.desc()).limit(2)
            info['rank'] = (page - 1) * 10 + index + 1
            info['commit'] = [cc.todict() for cc in commit_info]
            res['items'].append(info)
        return jsonify(res)


bp.add_url_rule('/someone', view_func=Hacker.as_view('one_hacker'))
bp.add_url_rule('/owned-planets/<string:username>', view_func=OwnedPlanets.as_view('owned_planets'))
bp.add_url_rule('/builded-planets/<string:username>', view_func=BuildedPlanets.as_view('builded_planets'))
bp.add_url_rule('/github-contribute', view_func=GithubContribute.as_view('github_contribute'))
bp.add_url_rule('/github-contribute-by-chain',
                view_func=SearchContributorByChainName.as_view('github_contribute_by_chain'))
