from elasticsearch import Elasticsearch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from seshat.config import Config


app = Flask(__name__)
app.config.from_object(Config)


app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    if app.config['ELASTICSEARCH_URL'] else None

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from seshat.models import User, Book, Author, load_user

mail = Mail(app)

admin = Admin(app)


class NewModelView(ModelView):
    def is_accessible(self):
        try:
            return current_user.is_admin == 1 and not current_user.is_anonymous
        except AttributeError:
            return False


admin.add_view(NewModelView(User, db.session))
admin.add_view(NewModelView(Book, db.session))
admin.add_view(NewModelView(Author, db.session))

from seshat import routes, errors
