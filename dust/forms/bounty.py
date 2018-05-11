from datetime import datetime, timedelta
from wtforms import StringField, Field, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError, NumberRange, URL

from . import JSONForm
from ..core import current_user, db
from ..models.user_planet import BountyReward, User
from ..constants import Status


class SetupBountyRewardForm(JSONForm):
    name = Field('name', [DataRequired(), Length(max=20, min=1)])
    description = StringField('description', [DataRequired(), Length(min=1)])
    keywords = StringField('team')
    email = StringField('email', [Email()])

    def __init__(self, uid=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = uid or current_user.id

    def validate_name(self, field):
        e = BountyReward.query.filter_by(name=field.data).first()
        if e:
            raise ValidationError('Duplicate BountyReward name')

    def save(self, pid=None):
        if pid:
            p = BountyReward.query.get_or_404(pid)
        else:
            p = BountyReward(owner_id=self.uid)
            db.session.add(p)
            p.dust_num = 500
        p.name = self.name.data
        p.description = self.description.data
        p.keywords = self.keywords.data
        p.email = self.email.data
        db.session.commit()
        return p

    def setup(self, owner_id=None):
        if owner_id:
            owner = User.query.get_or_404(owner_id)
        else:
            owner = current_user
        owner.owned_dust += 500
        return self.save()

