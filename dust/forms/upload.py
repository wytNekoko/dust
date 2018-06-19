from wtforms import StringField, Field, SelectField
from wtforms.validators import DataRequired, Length
from . import JSONForm
from ..core import current_user, db, redis_store
from ..models.user_planet import User
from ..constants import Role
from ..exceptions import LoginRequired


class AttenderForm(JSONForm):
    name = Field('name', [DataRequired(), Length(max=20, min=1)])
    city = StringField('city', [DataRequired(), Length(max=500, min=1)])
    role = SelectField('role', [DataRequired()], coerce=int, choices=[
        (Role.EXTRA, 'Hacker'),
        (Role.FULL_STACK, 'Full-Stack'),
        (Role.DAPPS, 'DApp'),
        (Role.DESIGNER, 'Designer'),
        (Role.PUBLIC_CHAIN, 'Public-Chain'),
        (Role.SECURITY, 'Security')
    ])
    org = StringField('org', [DataRequired(), Length(min=1)])
    eth = StringField('eth', [DataRequired(), Length(min=5)])
    slogan = StringField('slogan')

    def __init__(self, uid=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, uid=None):
        if uid:
            p = User.query.get_or_404(uid)
        else:
            raise LoginRequired()
        p.realname = self.name.data
        p.city = self.city.data
        p.role = self.role.data
        p.organization = self.org.data
        p.eth = self.eth.data
        p.slogan = self.slogan.data
        db.session.commit()
        return p


