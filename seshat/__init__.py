# from elasticsearch import Elasticsearch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from seshat.config import Config
from flask_restful import Api
# from seshat.models import User, Book, Author


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
admin = Admin()
api = Api()

from seshat import views


class NewModelView(ModelView):
    def is_accessible(self):
        try:
            return current_user.is_admin == 1 and not current_user.is_anonymous
        except AttributeError:
            return False


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    admin.init_app(app)
    api.init_app(app)

    # app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    #     if app.config['ELASTICSEARCH_URL'] else None

    # admin.add_view(NewModelView(User, db.session))
    # admin.add_view(NewModelView(Book, db.session))
    # admin.add_view(NewModelView(Author, db.session))

    from seshat.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from seshat.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from seshat.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app


from seshat import models
