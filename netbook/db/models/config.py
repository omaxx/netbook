import mongoengine as me

from netbook.logger import logger
from .inventory import Device


class Config(me.Document):
    device = me.ReferenceField(Device, required=True, reverse_delete_rule=me.CASCADE)
    text = me.StringField(required=True)


def add_config(device, **kwargs):
    logger.debug(f"{device} add_config with {kwargs}")
    return Config(**kwargs, device=device).save()


def add_config_list(device, config_list):
    for config in config_list:
        add_config(**config, device=device)


Device.add_config = add_config
Device.add_config_list = add_config_list
