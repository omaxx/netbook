from http import HTTPStatus

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from netbook import db
from . import schema

bp = Blueprint("folders-api", __name__)


class FolderView(MethodView):
    @staticmethod
    def folder(path):
        try:
            return db.Folder.get(path=path)
        except db.DoesNotExist:
            abort(HTTPStatus.NOT_FOUND)


@bp.route("/<path>/folders")
@bp.route("/folders")
class FolderList(FolderView):
    @bp.response(HTTPStatus.OK, schema.Folder(many=True))
    def get(self, path=None):
        """List sub-folders in folder"""
        return self.folder(path).list_folders()

    @bp.arguments(schema.Folder, as_kwargs=True)
    @bp.response(HTTPStatus.CREATED, schema.Folder)
    def post(self, path=None, **kwargs):
        """Create new sub-folder in folder"""
        return self.folder(path).create_folder(**kwargs)


@bp.route("/<path>/devices")
@bp.route("/devices")
class DeviceList(FolderView):
    @bp.response(HTTPStatus.OK, schema.Device(many=True))
    def get(self, path=None):
        """List devices in folder"""
        return self.folder(path).list_devices()

    @bp.arguments(schema.Device, as_kwargs=True)
    @bp.response(HTTPStatus.CREATED, schema.Device)
    def post(self, path=None, **kwargs):
        """Create new device in folder"""
        return self.folder(path).create_device(**kwargs)
