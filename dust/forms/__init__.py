from flask import request
from wtforms import Form
# from ..core import current_user


class JSONForm(Form):
    class Meta:
        locales = ['en']

    def __init__(self, item=None, data=None):
        if data is None:
            data = request.get_json()
        super().__init__(data=data)


class FForm(Form):
    class Meta:
        locales = ['en']

    def __init__(self):
        super().__init__(request.form)
