from flask import Blueprint

bp = Blueprint('users', __name__)


@bp.route('/')
def home():
    return "Users Blueprint"
