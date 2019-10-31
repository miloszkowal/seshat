from elasticsearch import Elasticsearch

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config['SECRET_KEY'] = 'bcdca3e428f8eadc6d04761ceace3204'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['ELASTICSEARCH_URL'] = 'http://localhost:9200'


app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    if app.config['ELASTICSEARCH_URL'] else None

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from seshat.models import User, Book

admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Book, db.session))

from seshat import routes
