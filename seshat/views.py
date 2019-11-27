from seshat import admin, db
from flask_admin.contrib.sqla import ModelView
from seshat.models import Author, Book, User, Genre, Language, Subject

admin.add_view(ModelView(Author, db.session))
admin.add_view(ModelView(Book, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Genre, db.session))
admin.add_view(ModelView(Language, db.session))
admin.add_view(ModelView(Subject, db.session))
