from . import config
from . import logger

from . import db


def init(**kwargs):
    settings = config.load()

    logger.init(**settings.get('logger', {}))
    db.mongo.connect(**settings.get('mongo', {}))

    return settings
