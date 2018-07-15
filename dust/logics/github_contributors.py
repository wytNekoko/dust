from ..core import db
from ..models.user_planet import *


def github_gift():
    crs = ContributeRecord.query.all()
    for cr in crs:
        github_commit = cr.commit / CoinGithub.query.filter_by(github_project_name=cr.github_project_name).commit_count
        coin = CoinPrice.query.filter_by(name=cr.chain_name)
        arr = CoinPrice.query.order_by(CoinPrice.price.desc())
        coin_price_rank = arr.index(coin) + 1
        tmp = Contributor.query.filter_by(author_login=cr.author_login)
        if not tmp:
            author = Contributor(author_login=cr.author_login, author_avatar=cr.author_avatar, score=0)
            author.score += (1/coin_price_rank) * github_commit
            db.session.add(author)
        else:
            tmp.score += (1/coin_price_rank) * github_commit
        db.session.flush()
    db.session.commit()
