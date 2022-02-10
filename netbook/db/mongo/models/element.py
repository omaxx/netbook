import mongoengine as me

from . import BaseDocument


class Element(BaseDocument):
    name = me.StringField(unique=True)
