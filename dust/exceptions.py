import sys

current_module = sys.modules[__name__]


exceptions = [
    ('NoError', 0, 'OK'),
    ('LoginRequired', 1001, '需要登录'),
    ('LoginInfoRequired', 1002, '用户名密码不能为空'),
    ('LoginInfoError', 1003, '用户名或密码错误'),
    ('NoPermission', 1004, '没有权限'),
    ('NoData', 1005, '数据不存在'),
    ('SystemRoleCanNotEdit', 1101, '系统角色不可编辑'),
    ('SystemRoleCanNotDelete', 1102, '系统角色不可删除'),
    ('RoleHasEmployeesCanNotDelete', 1103, '该角色下还有工作人员'),
    ('APITokenError', 9001, 'API Token Error.'),
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
