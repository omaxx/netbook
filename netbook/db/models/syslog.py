from datetime import datetime

import mongoengine as me

from netbook.logger import logger
from .inventory import Device


class Syslog(me.Document):
    device = me.ReferenceField(Device, required=True, reverse_delete_rule=me.CASCADE)
    message = me.StringField(required=True)


def add_syslog(device, **kwargs):
    logger.debug(f"{device} add_syslog with {kwargs}")
    return Syslog(**kwargs, device=device).save()


def add_syslog_list(device, syslog_list):
    for syslog in syslog_list:
        add_syslog(**syslog, device=device)


def get_syslog_list(
        device,
        ts_begin: datetime,
        ts_end: datetime,
        match: dict = None
):
    match = match or {}
    pipeline = [
        {
            "$match": {
                "$and": [
                    {"device": device.pk},
                    {"timestamp": {"$gte": ts_begin}},
                    {"timestamp": {"$lt": ts_end}},
                ]
            }
        },
        {
            "$match": match
        },
    ]

    return Syslog.objects.aggregate(pipeline)


def get_syslog_aggregate(
        device,
        ts_begin: datetime,
        ts_end: datetime,
        aggregate_time: int,
        match: dict = None,
):
    match = match or {}
    pipeline = [
        {
            "$match": {
                "$and": [
                    {"device": device.pk},
                    {"timestamp": {"$gte": ts_begin}},
                    {"timestamp": {"$lt": ts_end}},
                ]
            }
        },
        {
            "$match": match
        },
        {
            "$group": {
                "_id": {
                    "$dateTrunc": {
                        "date": "$timestamp",
                        "unit": "minute",
                        "binSize": aggregate_time,
                    }
                },
                "count": {"$sum": 1}
            }
        },
        # {"$addFields": {"from": "$_id"}},
        {"$sort": {"_id": 1}},
    ]
    return Syslog.objects.aggregate(pipeline) or [{"_id": ts_begin, "count": 0}]


Device.add_syslog = add_syslog
Device.add_syslog_list = add_syslog_list
