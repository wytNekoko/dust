import random

from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash
from ..core import db
from . import TimestampMixin


team_user_table = db.Table(
    'teammates', db.Model.metadata,
    db.Column('team_id', db.Integer, db.ForeignKey('team.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    )


class Team(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True, default=lambda: random.randint(1000001, 9999999),
                   comment='auto-generated random 7-digit-number')
    name = db.Column(db.String(20), nullable=False, default='', comment='<=20 character')
    # many-to-many
    users = db.relationship('User', secondary=team_user_table)


class User(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True, default=lambda: random.randint(1000001, 9999999),
                   comment='auto-generated random 7-digit-number')
    username = db.Column(db.String(20), nullable=False, default='', unique=True)
    _password = db.Column('password', db.String(191), comment='password')
    # email = db.Column(db.String(191), nullable=False, default='')
    owned_dust = db.Column(db.Integer, nullable=False, default=5000, comment='<=20 character')
    is_hacker = db.Column(db.Boolean, nullable=False, default=True, comment='False for investor')
    is_captain = db.Column(db.Boolean, nullable=False, default=True)

    build_reward_dust = db.Column(db.Integer, nullable=False, default=0)
    planet_dust_sum = db.Column(db.Integer, nullable=False, default=0, comment='Dust sum of owned planets')

    # one-to-many
    owned_planets = db.relationship('Planet')
    suggestions = db.relationship('Suggestion')
    # many-to-many
    teams = db.relationship('Team', secondary=team_user_table)

    @hybrid_property
    def password(self):
        return self._password
        # raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()


class Planet(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, default='', comment='<=20 character')
    description = db.Column(db.String(5000))
    demo_url = db.Column(db.String(191))
    github_url = db.Column(db.String(191))
    team_intro = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dust_num = db.Column(db.Integer, nullable=False, default=0)
    email = db.Column(db.String(191), nullable=False, default='')
    reward = db.Column(db.Integer, nullable=False, default=0, comment='Reward for the owner after liquidation')


class BuildRecord(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    builder_id = db.Column(db.Integer, nullable=False, default=0)
    planet_id = db.Column(db.Integer, nullable=False, default=0)
    dust_num = db.Column(db.Integer, nullable=False, default=0, comment='Dust for single build')
    planet_dust = db.Column(db.Integer, nullable=False, default=0, comment='Current dust sum of the planet')
    reward = db.Column(db.Integer, nullable=False, default=0, comment='Reward after liquidation')


class Suggestion(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.TEXT, nullable=False, default='')
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
