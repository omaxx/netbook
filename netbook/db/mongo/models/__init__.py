from .inventory import Object, Folder, Group, Device
from .config import Config
from .syslog import Syslog

import mongoengine as me
from netbook.db import errors


class BaseDocument(me.Document):
    meta = {
        'abstract': True,
    }

    @classmethod
    def get(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except me.DoesNotExist:
            raise errors.DoesNotExist()

    @classmethod
    def create(cls, **kwargs):
        try:
            return cls(**kwargs).save()
        except me.NotUniqueError:
            raise errors.AlreadyExist()

    @classmethod
    def list(cls, **kwargs):
        return cls.objects(**kwargs)


from .element import Element
from .component import Component
from .event import Event
from .users import User
