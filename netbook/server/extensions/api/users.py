from http import HTTPStatus

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from netbook import db
from . import schema

bp = Blueprint("users-api", __name__)
