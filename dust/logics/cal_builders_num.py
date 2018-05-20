from ..core import db
from ..models.user_planet import Planet, BuildRecord, User


def cal_builders():
    records = BuildRecord.query.all()
    for re in records:
        re.dust_num = int(re.dust_num/8.8)
        db.session.flush()
        p = Planet.query.get(re.planet_id)
        p.dust_num += re.dust_num
        p.builder_num += 1
        db.session.flush()
        re.planet_dust = p.dust_num
        db.session.flush()
    ps = Planet.query.all()
    for p in ps:
        u = User.query.get(p.owner_id)
        u.planet_dust_sum += p.dust_num
        db.session.flush()
    db.session.commit()
