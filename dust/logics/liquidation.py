from ..core import db
from ..models.user_planet import User, Planet, BuildRecord
from ..models.monthly_focus import TopBuilders, TopOwners, TopPlanets
from sqlalchemy import desc

BONUS = [10000, 8000, 6000, 3000, 3000, 1000, 1000, 1000, 1000, 1000]
# TODO: juxtaposition problem


def distribute(pid, amount):
    records = BuildRecord.query.filter_by(planet_id=pid).all()
    denominator = 0
    for record in records:
        factor = 100 / record.planet_dust
        denominator += record.dust_num * factor

    for record in records:
        factor = 100 / record.planet_dust
        builder = User.query.get(record.builder_id)
        income = amount * record.dust_num * factor / denominator
        builder.owned_dust += income
        builder.build_reward_dust += income
        record.reward = income


def liquidate():
    plist = Planet.query.order_by(desc(Planet.dust_num)).limit(10)
    print(plist)
    for i in range(plist.count()):
        p = TopPlanets(pid=plist[i].id, pname=plist[i].name, pdust=plist[i].dust_num)
        db.session.add(p)
        reward = plist[i].dust_num + BONUS[i]
        owner = User.query.get(plist[i].owner_id)
        portion = reward * 0.4
        owner.owned_dust += portion
        plist[i].reward += portion
        distribute(pid=plist[i].id, amount=reward*0.6)
    db.session.commit()
    liquidate_rest_planets(plist)


def liquidate_rest_planets(plist):
    planets = Planet.query.all()
    for p in planets:
        if p not in plist:
            owner = User.query.get(p.owner_id)
            owner.owned_dust += p.dust_num * 0.4
            distribute(pid=p.id, amount=p.dust_num*0.6)
    db.session.commit()


def get_monthly_focus():
    builder_list = User.query.order_by(desc(User.build_reward_dust)).limit(10)
    for b in builder_list:
        bb = TopBuilders(bid=b.id, bname=b.username, bdust=b.build_reward_dust)
        db.session.add(bb)

    owner_list = User.query.order_by(desc(User.planet_dust_sum)).limit(10)
    for o in owner_list:
        oo = TopOwners(oid=o.id, oname=o.username, odust=o.planet_dust_sum)
        db.session.add(oo)
    db.session.commit()

