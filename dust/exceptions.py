import sys

current_module = sys.modules[__name__]


exceptions = [
    # ('NoError', 0, 'OK'),
    # ('LoginRequired', 1001, 'Login is required.'),
    # ('LoginInfoRequired', 1002, 'username and password cannot be empty.'),
    # ('LoginInfoError', 1003, 'Wrong username or password.'),
    # ('NoPermission', 1004, 'No permission.'),
    # ('NoData', 1005, 'No such record.'),
    # ('LoginAuthError', 1006, 'Can\'t get access to github correctly'),
    # ('RegisterError', 1007, 'Can\'t get access to github correctly'),
    # ('DuplicateGithubUser', 1008, 'This github account/username has been registered. Please login directly.'),
    # ('RegisterFailError', 1009, 'This github account hasn\'t been registered correctly. Please register again.'),
    # ('NoTeam', 1010, 'Current user is not in a team.'),
    # ('FileRequired', 1011, 'No file in request'),
    # ('UnSupportFileType', 1012, 'Unsupported file type'),
    # ('EmptyUserInfo', 1013, 'Current user is Nonetype'),
    # ('NoDust', 1014, 'Not enough gift you owned'),
    # ('NoVote', 1015, '3 votes ran out. Your team\'s voting has ended.'),
    # ('TooManyVotes', 1016, 'Your team have voted for the team too many times.'),
    # ('VoteSelfError', 1017, 'To vote yourself is not allowed'),
    # ('VoteDAppError', 1018, 'Only ONE vote for ONE DApp is allowed.'),
    # ('SystemRoleCanNotEdit', 1101, 'System role cannot be edited.'),
    # ('SystemRoleCanNotDelete', 1102, 'System role cannot be deleted.'),
    # ('APITokenError', 9001, 'API Token Error.'),
    # ('CacheTokenError', 9002, 'Redis Cache Error.'),
    # ('ResetTokenError', 9003, 'Reset Token Redis Cache Error.'),
    ('NoError', 0, 'OK'),
    ('LoginRequired', 1001, '需要登录.'),
    ('LoginInfoRequired', 1002, 'CryptoName和密码不能为空.'),
    ('LoginInfoError', 1003, '错误的CryptoName或密码.'),
    ('NoPermission', 1004, '没有权限.'),
    ('NoData', 1005, '数据库中无此条记录.'),
    ('LoginAuthError', 1006, '无法连接到GitHub'),
    ('RegisterError', 1007, '连接GitHub时出错'),
    ('DuplicateGithubUser', 1008, '此GitHub账号已在本网站注册过，请直接登录.'),
    ('RegisterFailError', 1009, '此GitHub账号没有注册成功，请重新注册.'),
    ('NoTeam', 1010, '您不在一个队伍中.'),
    ('FileRequired', 1011, '缺少文件'),
    ('UnSupportFileType', 1012, '不支持该文件类型'),
    ('EmptyUserInfo', 1013, '无法取到当前用户信息'),
    ('NoDust', 1014, '您账户上的Gift余额不足'),
    ('NoVote', 1015, '您的队伍已经投出了三张票，不能再投了.'),
    ('TooManyVotes', 1016, '您的队伍已经投给该队伍两张票，不能再投了.'),
    ('VoteSelfError', 1017, '投给自己是不对的'),
    ('VoteDAppError', 1018, '您只能投给一个DApp'),
    ('EmailRequired', 1019, '需要填email'),
    ('NoEmailError', 1020, '这个email没有注册过哦'),
    ('SystemRoleCanNotEdit', 1101, 'System role cannot be edited.'),
    ('SystemRoleCanNotDelete', 1102, 'System role cannot be deleted.'),
    ('APITokenError', 9001, 'API Token Error.'),
    ('CacheTokenError', 9002, '缓存中没有您的token，请重新登录.'),
    ('ResetTokenError', 9003, 'Reset Token Redis Cache Error.'),
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
