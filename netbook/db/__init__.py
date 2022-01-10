import mongoengine as me
from .models import *
from .errors import *

DB_HOST = "localhost"
DB_NAME = "netbook"
# DB_USER_NAME = "root"
# DB_USER_PASSWORD = "root"

me.connect(
    host=DB_HOST,
    db=DB_NAME,
    # username=DB_USER_NAME,
    # password=DB_USER_PASSWORD,
    # authentication_source='admin',
)
