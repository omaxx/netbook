import logging

import mongoengine as me

logger = logging.getLogger(__name__)


def connect(db=None, host=None, username=None, password=None):
    db = db or __name__.split('.')[0]
    host = host or 'localhost'
    logger.info(f"mongo: connect to {db} on {host}")
    me.connect(
        host=host,
        db=db,
        username=username,
        password=password,
        authentication_source='admin',
    )


def disconnect():
    me.disconnect()
