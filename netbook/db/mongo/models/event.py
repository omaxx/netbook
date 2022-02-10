import mongoengine as me

from . import BaseDocument, Element


class Event(BaseDocument):
    element = me.ReferenceField(Element)
