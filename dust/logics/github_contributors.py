from ..core import db
from ..models.user_planet import *
import math


def get_rank():
    arr = CoinPrice.query.order_by(CoinPrice.price.desc()).all()
    for index, coin in enumerate(arr):
        x = CoinRank.query.filter_by(name=coin.name).first()
        if not x:
            rank = CoinRank(name=coin.name, rank=index + 1)
            db.session.add(rank)
        else:
            x.rank = index + 1
    db.session.commit()


def github_score():
    crs = ContributeRecord.query.all()
    for cr in crs:
        project = CoinGithub.query.filter_by(github_project_name=cr.github_project_name).first()
        github_commit = cr.commit / project.commit_count
        x = CoinRank.query.filter_by(name=cr.chain_name).first()
        if not x:
            continue
        coin_price_rank = x.rank
        tmp = Contributor.query.filter_by(author_login=cr.author_login).first()
        if not tmp:
            author = Contributor(author_login=cr.author_login, author_avatar=cr.author_avatar, score=0)
            db.session.add(author)
            author.score = (1/coin_price_rank) * github_commit * 100000000
            author.total_commit = cr.commit
        else:
            tmp.score += (1/coin_price_rank) * github_commit * 100000000
            tmp.total_commit += cr.commit
        db.session.flush()
    db.session.commit()


def cal_gift():
    TOTAL_GIFT = 700000 / 7
    section = [0.01, 0.05, 0.15, 0.3, 0.5, 0.75, 1]
    gift_portion = [0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.1]
    contributors = Contributor.query.order_by(Contributor.score.desc()).all()
    num = len(contributors)
    sec_index = [math.floor(num*s) for s in section]
    sec_num = [sec_index[i+1]-sec_index[i] for i in range(0, 6)]
    sec_num.insert(0, sec_index[0])
    sec_gift = [TOTAL_GIFT * gift_portion[i] / sec_num[i] for i in range(0, 7)]
    j = 0
    for i in range(0, num):
        if i <= sec_index[j]:
            contributors[i].gift = sec_gift[j]
        else:
            j += 1
            contributors[i].gift = sec_gift[j]
    db.session.commit()
