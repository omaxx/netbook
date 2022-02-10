from http import HTTPStatus

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from netbook import db
from . import schema

bp = Blueprint("devices-api", __name__)


class DeviceView(MethodView):
    @staticmethod
    def device(path):
        try:
            return db.Device.get(path=path)
        except db.DoesNotExist:
            abort(HTTPStatus.NOT_FOUND)


@bp.route("/<path>")
class Device(DeviceView):
    @bp.response(HTTPStatus.OK, schema.Device)
    def get(self, path):
        """Get device info"""
        return self.device(path)


@bp.route("/<path>/syslog")
class DeviceSyslog(DeviceView):
    @bp.arguments(schema.Syslog(many=True))
    @bp.response(HTTPStatus.CREATED)
    def post(self, syslog_list, path):
        """Add syslog messages"""
        self.device(path).add_syslog_list(syslog_list)


@bp.route("/<path>/config")
class DeviceConfig(DeviceView):
    @bp.arguments(schema.Config(many=True))
    @bp.response(HTTPStatus.CREATED)
    def post(self, syslog_list, path):
        """Add device configuration"""
        self.device(path).add_config_list(syslog_list)
