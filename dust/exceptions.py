import sys

current_module = sys.modules[__name__]


exceptions = [
    ('NoError', 0, 'OK'),
    ('LoginRequired', 1001, 'Login is required.'),
    ('LoginInfoRequired', 1002, 'username and password cannot be empty.'),
    ('LoginInfoError', 1003, 'Wrong username or password.'),
    ('NoPermission', 1004, 'No permission.'),
    ('NoData', 1005, 'No such record.'),
    ('SystemRoleCanNotEdit', 1101, 'System role cannot be edited.'),
    ('SystemRoleCanNotDelete', 1102, 'System role cannot be deleted.'),
    ('APITokenError', 9001, 'API Token Error.'),
    ('NoDust', 1006, 'Not enough dusts you owned')
]


class BaseCustomException(Exception):
    errcode = 1000
    errmsg = 'Server Unkown Error.'

    def __init__(self, errmsg=None, errcode=None, **kw):
        if errmsg:
            self.errmsg = errmsg
        if errcode is not None:
            self.errcode = errcode
        self.kw = kw

    def __str__(self):
        return '%d: %s' % (self.errcode, self.errmsg)

    def __repr__(self):
        return '<%s \'%s\'>' % (self.__class__.__name__, self)


class CustomException(BaseCustomException):
    pass


for name, errcode, errmsg in exceptions:
    cls = type(name,
               (CustomException,),
               {'errcode': errcode, 'errmsg': errmsg})
    setattr(current_module, name, cls)


class FormValidationError(BaseCustomException):
    errcode = 2001
    errmsg = '表单验证错误'

    def __init__(self, form, errmsg=None, show_first_err=True):
        if not errmsg and show_first_err:
            errmsg = next(iter(form.errors.values()))[0]
        super(FormValidationError, self).__init__(errmsg)
        self.errors = form.errors
