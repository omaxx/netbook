import mongoengine as me

from . import BaseDocument, Element


class Location(me.EmbeddedDocument):
    element = me.ReferenceField(Element)
    slot = me.StringField()


class Component(BaseDocument):
    name = me.StringField(unique=True)
    location = me.EmbeddedDocumentField(Location)
