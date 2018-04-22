from flask import Blueprint
from flask.views import MethodView

from ..forms.register import UserRegisterForm
from ..exceptions import FormValidationError


bp = Blueprint('register', __name__)


class RegisterView(MethodView):
    def post(self):
        form = UserRegisterForm()
        if form.validate():
            user = form.save()
            return user.todict()
        else:
            raise FormValidationError


bp.add_url_rule('/register', view_func=RegisterView.as_view('user_register'))
