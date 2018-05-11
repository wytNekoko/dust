from ..core import db
from ..models.user_planet import Planet, BuildRecord


def cal_builders():
    records = BuildRecord.query.all()
    for re in records:
        p = Planet.query.get(re.planet_id)
        p.builder_num += 1
    db.session.commit()