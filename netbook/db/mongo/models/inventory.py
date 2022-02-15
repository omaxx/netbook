from __future__ import annotations
import logging

import enum
from datetime import datetime

import mongoengine as me

from netbook.db.errors import DoesNotExist, AlreadyExist

SEPARATOR = "."
logger = logging.getLogger(__name__)


class Object(me.Document):
    name = me.StringField(required=True, regex=f"[^{SEPARATOR}]*")
    path = me.StringField(unique=True)
    folder = me.ReferenceField("Folder")

    title = me.StringField()
    description = me.StringField()

    meta = {
        'allow_inheritance': True,
        'collection': 'inventory',
        'indexes': [
            {'fields': ['name', 'folder'], 'unique': True, 'cls': False}
        ]
    }

    def __repr__(self):
        return f"<{self.__class__.__name__}: name: {self.name} ({self.path}), id: {self.pk}>"

    def __str__(self):
        return self.title or self.name

    def save(self, *args, **kwargs):
        if self.folder:
            self.path = self.folder.path + SEPARATOR + self.name
        else:
            self.path = self.name
        return super().save(*args, **kwargs)

    @classmethod
    def get(cls,
            path: str = None,
            name: str = None,
            folder: str = None,
            create: bool = False,
            **kwargs,
            ):
        if path is not None:
            if name is not None:
                raise TypeError("Please specify path OR name")
            else:
                path = folder + SEPARATOR + path if folder is not None else path
        else:
            if name is None:
                raise TypeError("Please specify path OR name")
            else:
                path = folder + SEPARATOR + name if folder is not None else name
        if cls in [Object, Folder] and path in [None, ""]:
            return RootFolder()
        try:
            return cls.objects.get(path=path)
        except me.DoesNotExist:
            logger.debug(f"db: {cls.__name__} with path={path} not found")
            if not create:
                raise DoesNotExist(f"{cls.__name__} with path=\"{path}\" not found") from None
            else:
                folder_path = SEPARATOR.join(path.split(SEPARATOR)[:-1])
                object_name = SEPARATOR.join(path.split(SEPARATOR)[-1:])
                logger.debug(f"db: going to create {cls.__name__}(name={object_name}) in Folder(path={folder_path})")
                obj = cls(
                    name=object_name,
                    folder=Folder.get(path=folder_path, create=True).self(),
                    **kwargs,
                ).save()
                logger.info(f"db: {cls.__name__} {object_name} was created in folder {folder_path}")
                return obj

    def parents(self):
        if self.path is None:
            return []
        path = self.path.split(SEPARATOR)
        return [SEPARATOR.join(path[0:i]) for i in range(1, len(path)+1)]


class Folder(Object):
    def self(self):
        return self

    def save(self, *args, **kwargs):
        old_path = self.path
        super().save(*args, **kwargs)
        if old_path and old_path != self.path:
            for obj in Object.objects(folder=self.self()):
                obj.save()
        return self

    def list_folders(self):
        return Folder.objects(folder=self.self())

    def list_groups(self):
        return Group.objects(folder=self.self())

    def list_devices(self):
        return Device.objects(folder=self.self())

    def create_folder(self, **kwargs):
        try:
            kwargs.pop("folder", None)
            return Folder(**kwargs, folder=self.self()).save()
        except me.NotUniqueError:
            raise AlreadyExist()

    def create_group(self, **kwargs):
        try:
            kwargs.pop("folder", None)
            return Group(**kwargs, folder=self.self()).save()
        except me.NotUniqueError:
            raise AlreadyExist()

    def create_device(self, **kwargs):
        try:
            kwargs.pop("folder", None)
            return Device(**kwargs, folder=self.self()).save()
        except me.NotUniqueError:
            raise AlreadyExist()

    def count_devices(self, direct_only=False):
        if direct_only:
            result = list(Device.objects(folder=self.self()).aggregate(count_pipeline))
        else:
            result = list(Device.objects(path__startswith=self.path+".").aggregate(count_pipeline))
        if result:
            return result[0]
        else:
            return {field['name']: 0 for field in count_fields}


class RootFolder(Folder):
    def self(self):
        return None

    def save(self, *args, **kwargs):
        pass


class Group(Object):
    def list_devices(self):
        return Device.objects(groups__in=[self])

    def add_device(self, device: Device):
        if self not in device.groups:
            device.update(push__groups=self)

    def remove_device(self, device: Device):
        if self in device.groups:
            device.update(pull__groups=self)

    def count_devices(self):
        result = list(Device.objects(groups__in=[self]).aggregate(count_pipeline))
        if result:
            return result[0]
        else:
            return {field['name']: 0 for field in count_fields}


count_fields = [
    {
        "name": "total",
        "condition": {}
    },
    {
        "name": "poll_status_ok",
        "condition": {"$eq": ["$poll_status.value", 'OK']}
    },
    {
        "name": "poll_status_error",
        "condition": {"$in": ["$poll_status.value", ['CONNECT_ERROR', 'AUTH_ERROR']]}
    },
    {
        "name": "state_normal",
        "condition": {"$eq": ["$state.value", 'NORMAL']}
    },
    {
        "name": "state_warning",
        "condition": {"$eq": ["$state.value", 'WARNING']}
    },
    {
        "name": "state_error",
        "condition": {"$eq": ["$state.value", 'ERROR']}
    },
]


count_pipeline = [
    {
        '$group': {
            '_id': None,
            **{
                field['name']: {
                    '$sum': {
                        '$cond': {'if': field['condition'], 'then': 1, 'else': 0}
                    }
                }
                for field in count_fields},
        },
    },
    {
        '$unset': '_id'
    },
]


class DevicePollStatus(enum.IntEnum):
    CREATED = 1
    DISABLED = 2
    ARCHIVED = 3
    OK = 0
    CONNECT_ERROR = -1
    AUTH_ERROR = -2


class DeviceState(enum.IntEnum):
    UNKNOWN = 1
    NORMAL = 0
    WARNING = -1
    ERROR = -2
    CRITICAL = -3


class DevicePollStatusField(me.EmbeddedDocument):
    # value = me.EnumField(DeviceStatus, default=DeviceStatus.CREATED)
    value = me.StringField(default="CREATED", choices=[status.name for status in DevicePollStatus])
    updated = me.DateTimeField(default=datetime.utcnow)
    last_ok = me.DateTimeField()


class DeviceStateField(me.EmbeddedDocument):
    # value = me.EnumField(DeviceState, default=DeviceState.UNKNOWN)
    value = me.StringField(default="UNKNOWN", choices=[state.name for state in DeviceState])
    updated = me.DateTimeField(default=datetime.utcnow)
    last_normal = me.DateTimeField()


# class DeviceVars(me.EmbeddedDocument):
#     ip = me.StringField()
#
#
class DeviceInfo(me.EmbeddedDocument):
    hostname = me.StringField()
    model = me.StringField()
    family = me.StringField()


class Device(Object):
    groups = me.ListField()
    poll_status = me.EmbeddedDocumentField(DevicePollStatusField, default=DevicePollStatusField)
    state = me.EmbeddedDocumentField(DeviceStateField, default=DeviceStateField)
    # vars = me.EmbeddedDocumentField(DeviceVars)
    vars = me.DictField()
    info = me.EmbeddedDocumentField(DeviceInfo)

    def update_poll_status(self, value, updated=None):
        if updated is None:
            updated = datetime.utcnow()
        if updated < self.poll_status.updated:
            return False
        self.poll_status.value = value
        self.poll_status.updated = updated
        if updated == "OK":
            self.poll_status.last_ok = updated
        self.save()
        return True

    def update_state(self, value, updated=None):
        if updated is None:
            updated = datetime.utcnow()
        if updated < self.state.updated:
            return False
        self.state.value = value
        self.state.updated = updated
        if value == "NORMAL":
            self.state.last_normal = updated
        self.save()
        return True

