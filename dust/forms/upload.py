from wtforms import StringField, Field, FileField
from wtforms.validators import DataRequired, Length, URL
from flask import request

from . import FForm
from ..core.flask_oss import gen_filename
from ..core import current_user, db, redis_store, oss, logger
from ..models.user_planet import *
from ..constants import Role
from ..exceptions import LoginRequired, FileRequired, UnSupportFileType


def file_url(mimetype, data):
    if not mimetype.startswith('image/'):
        raise UnSupportFileType('不支持的文件类型', mimetype=mimetype)
    filename = 'images/' + gen_filename(mimetype)
    oss.bucket.put_object(filename, data, {'Content-Type': mimetype})
    url = f'{oss.domain_schema}://{oss.bucket.bucket_name}.{oss.domain}/{filename}'
    # 保存到数据库
    ur = UploadRecord(
        uid=current_user.id,
        mimetype=mimetype,
        filename=filename, url=url
    )
    db.session.add(ur)
    db.session.commit()
    return url


"""上传图片

.. code-block:: sh

    POST /upload/image

此接口不是传输json格式， 而是使用multipart/form-data格式

字段： file

返回::

    {"url": "图片的url"}
"""


def get_file(name):
    file_ = request.files[name]
    url = file_url(file_.mimetype, file_)
    return url


def get_files():
    files_ = request.files
    urls = [file_url(files_[f].mimetype, files_[f]) for f in files_.keys()]
    return urls


class AttenderForm(FForm):
    name = Field('name', [DataRequired(), Length(max=20, min=1)])
    city = StringField('city', [DataRequired(), Length(max=500, min=1)])
    role = StringField('role', [DataRequired()])
    org = StringField('org', [DataRequired(), Length(min=1)])
    eth = StringField('eth', [DataRequired(), Length(min=5)])
    slogan = StringField('slogan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self):
        if current_user:
            u = current_user
        else:
            raise LoginRequired()
        a = get_file('file')
        if a:
            u.avatar = a
        logger.debug('avatar url: '+u.avatar)
        u.hacker_name = self.name.data
        u.city = self.city.data
        u.role = self.role.data
        u.organization = self.org.data
        u.eth = self.eth.data
        if self.slogan.data:
            u.slogan = self.slogan.data
        u.is_hacker = True
        db.session.commit()
        return u


class ProjectForm(FForm):
    name = Field('name', [DataRequired(), Length(max=50, min=1)])
    git = StringField('git', [DataRequired(), URL()])
    desc = StringField('desc', [DataRequired()])
    demo = StringField('demo', [URL()])
    # logo = StringField('logo', [DataRequired(), URL()])
    # photos = Field('demo_photos', default=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set(self, pid):
        item = Project.query.get(pid)
        item.name = self.name.data
        item.git = self.git.data
        logo_url = get_file('logo')
        item.logo = logo_url
        item.description = self.desc.data
        logger.debug('project demo: %s', self.demo.data)
        if self.demo.data:
            item.demo = self.demo.data
            logger.debug('project demo: ', self.demo.data)
        else:
            logger.debug('request.files', request.files)
            logger.debug('request.files', request.files.keys())
        # urls = get_files()
        # for url in urls:
        #     logger.debug('project photo url: %s', url)
        #         d = DemoPhoto(url=url, project_id=pid)
        #         db.session.add(d)
        #         item.photos.append(d)
        db.session.add(item)
        db.session.commit()
        return item

    def create(self):
        p = Project(team_id=current_user.cteam_id)
        t = Team.query.get(current_user.cteam_id)
        for usr in t.users:
            usr.owned_dust += 100
        db.session.add(p)
        db.session.flush()
        return self.set(p.id)


class ProfileForm(FForm):
    city = StringField('city', [DataRequired(), Length(max=500, min=1)])
    email = StringField('email', [DataRequired()])
    gift = StringField('gift', [DataRequired(), Length(min=1)])
    eth = StringField('eth', [DataRequired(), Length(min=5)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self):
        if current_user:
            u = current_user
        else:
            raise LoginRequired()
        u.avatar = get_file('file')
        u.city = self.city.data
        u.email = self.email.data
        u.gift = self.gift.data
        u.eth = self.eth.data
        db.session.commit()
        return u