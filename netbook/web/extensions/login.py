from flask_login import LoginManager

from netbook import db


def create_app(server):

    login = LoginManager(server)
    login.login_view = 'login'

    @login.user_loader
    def load_user(idx):
        try:
            return db.User.get(id=idx)
        except db.errors.DoesNotExist:
            return None

    return login
