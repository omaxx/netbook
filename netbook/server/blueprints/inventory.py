from flask import Blueprint

bp = Blueprint('inventory', __name__)


@bp.route('/')
def home():
    return "Inventory Blueprint"
