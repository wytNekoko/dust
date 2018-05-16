from datetime import datetime, timedelta
from wtforms import StringField, Field, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError, NumberRange, URL

from . import JSONForm
from ..core import current_user, db
from ..models.user_planet import Suggestion, User
from ..constants import Status


class FeedbackForm(JSONForm):
    title = Field('title', [DataRequired(), Length(max=100, min=1)])
    content = StringField('content', [DataRequired(), Length(min=1)])
    type = StringField()
    email = StringField('email', [DataRequired(), Email()])

    def __init__(self, uid=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = uid or current_user.id

    def save(self, pid=None):
        if pid:
            p = Suggestion.query.get_or_404(pid)
        else:
            p = Suggestion(uid=self.uid)
        p.title = self.title.data
        p.content = self.content.data
        p.type = self.type.data
        p.email = self.email.data
        db.session.commit()
        return p

    def setup(self, owner_id=None):
        if owner_id:
            owner = User.query.get_or_404(owner_id)
        else:
            owner = current_user
        return self.save()

