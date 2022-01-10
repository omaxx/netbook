import marshmallow as ma


class Folder(ma.Schema):
    name = ma.fields.String(required=True)
    path = ma.fields.String(dump_only=True)


class PollStatus(ma.Schema):
    value = ma.fields.String()
    updated = ma.fields.DateTime()
    last_ok = ma.fields.DateTime(dump_only=True)


class State(ma.Schema):
    value = ma.fields.String()
    updated = ma.fields.DateTime()
    last_normal = ma.fields.DateTime(dump_only=True)


class Device(ma.Schema):
    name = ma.fields.String(required=True)
    path = ma.fields.String(dump_only=True)
    poll_status = ma.fields.Nested(PollStatus, dump_only=True)
    state = ma.fields.Nested(State, dump_only=True)


class Config(ma.Schema):
    text = ma.fields.String()
    timestamp = ma.fields.DateTime()


class Syslog(ma.Schema):
    message = ma.fields.String()
