from ..core import db
from . import TimestampMixin


class TopPlanets(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, comment='planet_id')
    pname = db.Column(db.String(20), comment='planet_name')
    pdust = db.Column(db.Integer, comment='planet_dust')


class TopBuilders(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    bid = db.Column(db.Integer, comment='builder_id')
    bname = db.Column(db.String(20), comment='builder_name')
    bdust = db.Column(db.Integer, comment='builder_reward_dust')


class TopOwners(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    oid = db.Column(db.Integer, comment='planet_owner_id')
    oname = db.Column(db.String(20), comment='planet_owner_name')
    odust = db.Column(db.Integer, comment='planet_dust_sum')
