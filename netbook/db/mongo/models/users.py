import mongoengine as me
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from . import BaseDocument


class User(UserMixin, BaseDocument):
    name = me.StringField(required=True, unique=True)
    password_hash = me.StringField(required=True)

    def __init__(self, **kwargs):
        if "password" in kwargs:
            kwargs["password_hash"] = generate_password_hash(kwargs.pop("password"))
        super().__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
