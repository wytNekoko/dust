from ..core import db
from ..models.user_planet import User, Planet, BuildRecord
from sqlalchemy import desc

REWARD = [10000, 8000, 6000, 3000, 3000, 1000, 1000, 1000, 1000, 1000]


def distribute(pid, amount):
    records = BuildRecord.query.filter_by(planet_id=pid).all()
    denominator = 0
    for record in records:
        factor = 500 / record.planet_dust
        denominator += record.dust_num * factor

    for record in records:
        factor = 500 / record.planet_dust
        builder = User.query.get(record.builder_id)
        income = amount * record.dust_num * factor / denominator
        builder.owned_dust += income
        builder.build_reward_dust += income


def liquidate():
    ret = list()
    plist = Planet.query.order_by(desc(Planet.dust_num)).limit(10)
    print(plist)
    for i in range(min(plist.count(), 10)):
        reward = plist[i].dust_num + REWARD[i]
        owner = User.query.get(plist[i].owner_id)
        owner.owned_dust += reward * 0.4
        distribute(pid=plist[i].id, amount=reward*0.6)
        ret.append({'name': plist[i].name, 'dust': plist[i].dust_num})
    db.session.commit()
    liquidate_rest_planets(plist)
    return ret


def liquidate_rest_planets(plist):
    planets = Planet.query.all()
    for p in planets:
        if p not in plist:
            # planet = Planet.query.get(p.id)
            owner = User.query.get(p.owner_id)
            owner.owned_dust += p.dust_num * 0.4
            distribute(pid=p.id, amount=p.dust_num*0.6)
    db.session.commit()
