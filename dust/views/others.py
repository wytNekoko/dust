from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from ..core import current_user
from ..forms.others import FeedbackForm
from ..exceptions import FormValidationError
from ..models.user_planet import Notification


bp = Blueprint('others', __name__)


class FeedbackView(MethodView):
    def post(self):
        form = FeedbackForm()
        if form.validate():
            p = form.setup()
            return p.todict()
        else:
            raise FormValidationError(form)


class GetNotificationView(MethodView):
    def get(self, uid):
        ns = Notification.query.filter_by(uid=uid).order_by(Notification.created_at.desc()).all()
        ret = list()
        for n in ns:
            x = n.todict()
            x['created_at'] = n.created_at
            ret.append(x)
        return jsonify(ret)


bp.add_url_rule('/feedback', view_func=FeedbackView.as_view('feedback'))
bp.add_url_rule('/notifications/<string:uid>', view_func=GetNotificationView.as_view('notification'))
