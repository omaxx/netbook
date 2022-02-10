from flask import Flask

import netbook


def create_app():
    settings = netbook.init()
    from .config import BaseConfig

    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    from . import routes

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app):
    from .extensions import login
    from .extensions import api
    from .extensions import dash

    login.create_app(app)
    api.create_app(app, url_prefix='/api')
    dash.create_app(app, url_prefix='/dash')


def register_blueprints(app):
    from .blueprints import inventory
    from .blueprints import users

    app.register_blueprint(inventory.bp, url_prefix='/inventory')
    app.register_blueprint(users.bp, url_prefix='/users')


