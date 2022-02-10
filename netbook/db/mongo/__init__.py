import mongoengine as me


def connect(**kwargs):
    me.connect(
        host=kwargs.get('host'),
        db=kwargs.get('db', __name__.split(".")[0]),
        username=kwargs.get('username'),
        password=kwargs.get('password'),
        authentication_source='admin',
    )


def disconnect():
    me.disconnect()
