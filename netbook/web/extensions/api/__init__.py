from flask_smorest import Api


def create_app(server, url_prefix):
    app = Api(server)
    register_blueprints(app, url_prefix)
    return app


def register_blueprints(app, url_prefix):
    from . import folders
    from . import devices
    from . import users

    app.register_blueprint(folders.bp, url_prefix=url_prefix+"/folders")
    app.register_blueprint(devices.bp, url_prefix=url_prefix+"/devices")
    app.register_blueprint(users.bp, url_prefix=url_prefix+"/users")
