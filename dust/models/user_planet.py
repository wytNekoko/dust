import random

from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash
from ..core import db
from . import TimestampMixin
from ..constants import *


class Activity(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, default='')
    like = db.Column(db.Integer, nullable=False, default=0)


team_user_table = db.Table(
    'teammates', db.Model.metadata,
    db.Column('team_id', db.Integer, db.ForeignKey('team.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    )


class Team(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True, default=lambda: random.randint(10001, 99999),
                   comment='auto-generated random 7-digit-number')
    name = db.Column(db.String(50), nullable=False, default='', comment='<=20 character')
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, comment='Current competition')
    # many-to-many
    users = db.relationship('User', secondary=team_user_table, back_populates='teams')
    # many-to-one
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    captain_id = db.Column(db.Integer, nullable=False, default=0)
    # one-to-many
    project = db.relationship('Project')
    votes = db.Column(db.SmallInteger, nullable=False, default=3, comment='number to vote')
    ballot = db.Column(db.SmallInteger, nullable=False, default=0, comment='received number')
    judges = db.Column(db.SmallInteger, nullable=False, default=0, comment='votes from judges')
    bonus = db.Column(db.Integer, nullable=False, default=0)


class Project(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='')
    git = db.Column(db.String(191), nullable=False, default='')
    description = db.Column(db.String(3000), nullable=False, default='')
    demo = db.Column(db.String(191), nullable=False, default='')
    logo = db.Column(db.String(191), nullable=False, default='', comment='url for logo')
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    photos = db.relationship('DemoPhoto', cascade="all, delete-orphan")


class DemoPhoto(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    url = db.Column(db.String(191), nullable=False, default='')

    def todict_simple(self):
        return self.url


class VoteRecord(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    from_tid = db.Column(db.Integer)
    to_tid = db.Column(db.Integer)


class Competition(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='')
    rules = db.Column(db.TEXT)
    time = db.Column(db.String(50))
    place = db.Column(db.String(70))
    teams = db.relationship('Team')


user_following = db.Table(
    'user_following', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('following_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True, default=lambda: random.randint(1000001, 9999999),
                   comment='auto-generated random 7-digit-number')
    username = db.Column(db.String(20), nullable=False, default='', unique=True)
    hacker_name = db.Column(db.String(20), nullable=False, default='')
    city = db.Column(db.String(500), nullable=False, default='')
    avatar = db.Column(db.String(191), nullable=False, default='https://dorahacks-fund.oss-us-west-1.aliyuncs.com/images/avatar-cat.jpg')
    _password = db.Column('password', db.String(191), comment='password')
    email = db.Column(db.String(191), nullable=False, default='')
    organization = db.Column(db.String(200), nullable=False, default='')
    owned_dust = db.Column(db.Integer, nullable=False, default=100, comment='<=20 character')
    is_hacker = db.Column(db.Boolean, nullable=False, default=False, comment='True for hackathon attenders')
    votes = db.Column(db.Integer, nullable=False, default=0, comment='number to vote for judge')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.String(20), nullable=False, default=Role.EXTRA, comment='Role of hacker')
    git_account = db.Column(db.String(191), nullable=False, default='')
    fb_account = db.Column(db.String(191), nullable=False, default='')
    github_link = db.Column(db.String(191), nullable=False, default='')
    build_reward_dust = db.Column(db.Integer, nullable=False, default=0)
    planet_dust_sum = db.Column(db.Integer, nullable=False, default=0, comment='Dust sum of owned planets')
    gift_addr = db.Column(db.String(150), nullable=False, default='NOT SAVE', comment='KCash Gift address')
    eth = db.Column(db.String(150), nullable=False, default='NOT SAVE', comment='Eth address')
    bch = db.Column(db.String(150), nullable=False, default='NOT SAVE', comment='Bch address')
    slogan = db.Column(db.String(500), nullable=False, default='', comment='Slogan for teaming up')
    invitation_code = db.Column(db.String(50), nullable=False, default='')
    # one-to-many
    owned_planets = db.relationship('Planet')
    suggestions = db.relationship('Suggestion')
    bounty_rewards = db.relationship('BountyReward')
    # many-to-many
    teams = db.relationship('Team', secondary=team_user_table, back_populates='users')
    cteam_id = db.Column(db.Integer, nullable=False, default=0, comment='Current team id')

    following = db.relationship('User', secondary=user_following,
                                primaryjoin=id==user_following.c.user_id,
                                secondaryjoin=id==user_following.c.following_id,
                                backref='followers')

    def follow(self, other):
        if other not in self.following:
            self.following.append(other)
            other.followers.append(self)

    def unfollow(self, other):
        if other in self.following:
            self.following.remove(other)
            other.followers.remove(self)

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

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


class Planet(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, default='', comment='<=20 character')
    keywords = db.Column(db.String(50), nullable=False, default='')
    description = db.Column(db.String(2000))
    demo_url = db.Column(db.String(191))
    github_url = db.Column(db.String(191))
    team_intro = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dust_num = db.Column(db.Integer, nullable=False, default=0)
    email = db.Column(db.String(191), nullable=False, default='')
    reward = db.Column(db.Integer, nullable=False, default=0, comment='Reward for the owner after liquidation')
    status = db.Column(db.Integer, nullable=False, default=Status.DEFAULT, comment='Normal or unshelved.')
    builder_num = db.Column(db.Integer, nullable=False, default=0, comment='builders')


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
    email = db.Column(db.String(191), nullable=False, default='')
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    type = db.Column(db.String(20))


class BountyReward(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True, default=lambda: random.randint(1000001, 9999999),
                   comment='auto-generated random 7-digit-number')
    name = db.Column(db.String(100), nullable=False, default='', comment='<=20 character')
    company_name = db.Column(db.String(50), nullable=False, default='')
    description = db.Column(db.TEXT, nullable=False, default='')
    keywords = db.Column(db.String(100), nullable=False, default='')
    background = db.Column(db.TEXT, nullable=False, default='')
    email = db.Column(db.String(191), nullable=False, default='')
    status = db.Column(db.SmallInteger, nullable=False, default=Status.DEFAULT)
    reward = db.Column(db.Integer, nullable=False, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Notification(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.TEXT, nullable=False, default='')
    from_uid = db.Column(db.Integer, nullable=False, default=0)
    to_uid = db.Column(db.Integer, nullable=False, default=0)
    type = db.Column(db.SmallInteger, nullable=False)
    status = db.Column(db.SmallInteger, nullable=False, default=Note.UNREAD)


class UploadRecord(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    mimetype = db.Column(db.String(200))
    filename = db.Column(db.String(200))
    url = db.Column(db.String(191))


class CoinPrice(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)


class CoinRank(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    rank = db.Column(db.Integer)


class CoinGithub(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    chain_name = db.Column(db.String(50))
    commit_count = db.Column(db.Integer)
    github_project_name = db.Column(db.String(100))
    github_project_url = db.Column(db.String(200))


class ContributeRecord(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    author_avatar = db.Column(db.String(191))
    author_id = db.Column(db.Integer)
    author_login = db.Column(db.String(50))
    chain_name = db.Column(db.String(50))
    commit = db.Column(db.Integer)
    add = db.Column(db.Integer)
    delete = db.Column(db.Integer)
    github_project_name = db.Column(db.String(100))


class Contributor(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    author_avatar = db.Column(db.String(191))
    author_login = db.Column(db.String(50))
    total_commit = db.Column(db.Integer)
    score = db.Column(db.Float)
    gift = db.Column(db.Integer)


class WithdrawRecord(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Integer)
    after = db.Column(db.Integer)


class TalkList(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    txt = db.Column(db.TEXT)
    time = db.Column(db.DateTime)
    readstate = db.Column(db.Boolean)
    isgroup = db.Column(db.Boolean)
    apply = db.Column(db.Boolean)


class MsgList(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.TEXT)
    read = db.Column(db.Integer)
    from_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    istalk = db.Column(db.Boolean)
    isgroup = db.Column(db.Boolean)




