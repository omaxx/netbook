import os

import mongoengine as me

from .models import *
from .errors import *

DB_HOST = "localhost"
DB_NAME = "netbook"
DB_USER_NAME = os.environ.get("MONGO_USER_NAME")
DB_USER_PASSWORD = os.environ.get("MONGO_USER_PASSWORD")

me.connect(
    host=DB_HOST,
    db=DB_NAME,
    username=DB_USER_NAME,
    password=DB_USER_PASSWORD,
    authentication_source='admin',
)
