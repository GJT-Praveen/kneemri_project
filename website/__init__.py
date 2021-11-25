from flask import Flask, current_app, request
from website.controllers import db
from flask_login import LoginManager, current_user
from website.models.user_list import User
from functools import wraps
from flask_uploads import configure_uploads,UploadSet,IMAGES

login_manager = LoginManager()
login_manager.login_view = '/login'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Quarkspark'
    db.connect()

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User(**db.get_user_for_userid(id)[0])

    from .controllers.views import views
    from .controllers.auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app


def login_with_role(role, *args, **kwargs):
    def login_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            elif current_user.get_usertype() not in role:
                return current_app.login_manager.unauthorized()
            elif current_app.config.get('LOGIN_DISABLED'):
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        return decorated_view
    return login_required
