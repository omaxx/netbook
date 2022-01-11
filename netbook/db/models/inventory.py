from __future__ import annotations

import enum
from datetime import datetime

import mongoengine as me

from ..errors import DoesNotExist, AlreadyExist

SEPARATOR = "."


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
    def get(cls, path=None):
        if cls in [Object, Folder] and path is None:
            return RootFolder()
        try:
            return cls.objects.get(path=path)
        except me.DoesNotExist:
            raise DoesNotExist(f"{cls.__name__} with path=\"{path}\" not found") from None


class Folder(Object):
    def save(self, *args, **kwargs):
        old_path = self.path
        super().save(*args, **kwargs)
        if old_path and old_path != self.path:
            for obj in Object.objects(folder=self):
                obj.save()
        return self

    def list_folders(self):
        return Folder.objects(folder=self)

    def list_groups(self):
        return Group.objects(folder=self)

    def list_devices(self):
        return Device.objects(folder=self)

    def create_folder(self, **kwargs):
        try:
            kwargs.pop("folder", None)
            return Folder(**kwargs, folder=self).save()
        except me.NotUniqueError:
            raise AlreadyExist()

    def create_group(self, **kwargs):
        try:
            kwargs.pop("folder", None)
            return Group(**kwargs, folder=self).save()
        except me.NotUniqueError:
            raise AlreadyExist()

    def create_device(self, **kwargs):
        try:
            kwargs.pop("folder", None)
            return Device(**kwargs, folder=self).save()
        except me.NotUniqueError:
            raise AlreadyExist()


class RootFolder(Folder):
    def save(self, *args, **kwargs):
        pass

    def list_folders(self):
        return Folder.objects(folder=None)

    def list_groups(self):
        return Group.objects(folder=None)

    def list_devices(self):
        return Device.objects(folder=None)

    def create_folder(self, **kwargs):
        try:
            kwargs.pop("folder", None)
            return Folder(**kwargs, folder=None).save()
        except me.NotUniqueError:
            raise AlreadyExist()

    def create_group(self, **kwargs):
        try:
            kwargs.pop("folder", None)
            return Group(**kwargs, folder=None).save()
        except me.NotUniqueError:
            raise AlreadyExist()

    def create_device(self, **kwargs):
        try:
            kwargs.pop("folder", None)
            return Device(**kwargs, folder=None).save()
        except me.NotUniqueError:
            raise AlreadyExist()


class Group(Object):
    def list_devices(self):
        return Device.objects(groups__in=[self])

    def add_device(self, device: Device):
        if self not in device.groups:
            device.update(push__groups=[self])

    def remove_device(self, device: Device):
        raise NotImplementedError()


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


class Device(Object):
    groups = me.ListField()
    poll_status = me.EmbeddedDocumentField(DevicePollStatusField, default=DevicePollStatusField)
    state = me.EmbeddedDocumentField(DeviceStateField, default=DeviceStateField)

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

