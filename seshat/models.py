from datetime import datetime

from seshat import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


book_ownership = db.Table('ownership',
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                          db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
                          db.Column('date_added', db.DateTime, nullable=False, default=datetime.utcnow())
                          )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    books = db.relationship('Book', secondary=book_ownership, lazy='subquery', backref=db.backref('owners', lazy='dynamic'))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    num_pages = db.Column(db.Integer)
    isbn = db.Column(db.String(100))

    def __repr__(self):
        return f"Book('{self.title}',' by {self.author}')"

    def __str__(self):
        return f"Book('{self.title}',' by {self.author}')"
