from wtforms import StringField, Field, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError

from . import JSONForm
from ..core import current_user, db
from ..models.user_planet import BountyReward, User


class SetupBountyRewardForm(JSONForm):
    name = Field('name', [DataRequired(), Length(max=100, min=1)])
    company_name = StringField()
    description = StringField('description', [DataRequired(), Length(min=1)])
    keywords = StringField('team')
    background = StringField()
    email = StringField('email', [Email()])
    reward = IntegerField('reward')

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
        p.name = self.name.data
        p.company_name = self.company_name.data
        p.description = self.description.data
        p.keywords = self.keywords.data
        p.background = self.background.data
        p.email = self.email.data
        p.reward = self.reward.data
        db.session.commit()
        return p

    def setup(self, owner_id=None):
        if owner_id:
            owner = User.query.get_or_404(owner_id)
        else:
            owner = current_user
        # owner.owned_dust += 500
        return self.save()

