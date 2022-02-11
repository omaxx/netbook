from . import config
from . import logger

from . import db


def init(**kwargs):
    settings = config.load()

    logger.init(level=settings.get('logger.level', 'INFO'))
    db.mongo.connect(
        db=settings.get("mongo.db"),
        host=settings.get("mongo.host"),
        username=settings.get("mongo.username"),
        password=settings.get("mongo.password"),
    )

    return settings
