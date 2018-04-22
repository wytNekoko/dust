from sqlalchemy.ext.declarative import declared_attr

from ..core import db


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return db.Column(db.DateTime, default=db.func.now())

    @declared_attr
    def updated_at(cls):
        return db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())