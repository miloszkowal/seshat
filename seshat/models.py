from time import time
from datetime import datetime

import jwt
from flask import current_app
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from seshat import db, login_manager
from seshat.search import add_to_index, remove_from_index, query_index


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

ownership = db.Table('ownership',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
                     db.Column('date_added', db.DateTime, default=datetime.utcnow)
                     )

authorship = db.Table('authorship',
                      db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
                      db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True)
                      )

book_subject = db.Table('book_subject',
                        db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
                        db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
                        )


class Tagging(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

    db.UniqueConstraint('user_id', 'book_id', 'tag_id')
    db.relationship('User', backref='tags', lazy='dynamic')
    db.relationship('Book', backref='tags', lazy='dynamic')
    db.relationship('Tag', backref='tags', lazy='dynamic')

    def __init__(self, user, book, tag):
        self.user_id = user.id
        self.book_id = book.id
        self.tag_id = tag.id

    def __repr__(self):
        return f"<Tagging({self.user_id},{self.book_id},{self.tag_id})>"


class User(SearchableMixin, db.Model, UserMixin):
    __searchable__ = ['username', 'email', 'first_name', 'last_name']
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Integer, default=0)
    books = db.relationship('Book', secondary=ownership, lazy='subquery', backref=db.backref('owners', lazy='dynamic'))
    user_tags = db.relationship('Tagging', lazy='subquery', backref='user')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password):
        self.password = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Book(SearchableMixin, db.Model):
    __searchable__ = ['title', 'isbn', 'isbn_13']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    num_pages = db.Column(db.Integer)
    isbn = db.Column(db.String(100))
    isbn_13 = db.Column(db.String(20))
    publish_date = db.Column(db.DateTime)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    msrp = db.Column(db.Float)
    cover_image = db.Column(db.String(20), nullable=False, default='default_book.png')
    book_tags = db.relationship('Tagging', lazy='subquery', backref='book')

    def __repr__(self):
        return f"<Book('{self.title}')>"


class Genre(SearchableMixin, db.Model):
    __searchable__ = ['genre']
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), nullable=False)
    books = db.relationship('Book', backref='genre', lazy=True)

    def __repr__(self):
        return f"<Genre({self.genre})>"


class Author(SearchableMixin, db.Model):
    __searchable__ = ['first_name', 'last_name']
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    birth_date = db.Column(db.DateTime)
    death_date = db.Column(db.DateTime)
    books = db.relationship('Book', secondary=authorship, lazy='subquery', backref=db.backref('authors', lazy='dynamic'))

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Author({self.first_name} {self.last_name})>"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Publisher(SearchableMixin, db.Model):
    __searchable__ = ['org_name']
    id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(100), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    wiki_link = db.Column(db.String())
    website = db.Column(db.String())
    founded = db.Column(db.DateTime)
    books = db.relationship('Book', backref='publisher', lazy=True)

    def __repr__(self):
        return f"<Publisher({self.org_name})>"


class Language(db.Model):
    """
    Table for languages in ISO 639-1 Format
    """
    id = db.Column(db.Integer, primary_key=True)
    lang = db.Column(db.String(5), nullable=False)
    culture = db.Column(db.String(35))
    lang_code = db.Column(db.String(5))
    lang_name = db.Column(db.String(35))
    books = db.relationship('Book', backref='language', lazy=True)

    def __repr__(self):
        return f"<Language({self.lang})>"


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    books = db.relationship('Book', secondary=book_subject, lazy='subquery', backref=db.backref('subjects', lazy='dynamic'))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100), nullable=False)
    tag_tags = db.relationship('Tagging', lazy='subquery', backref='tag')

    def __repr__(self):
        return f"<Tag({self.tag})>"


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(5))  # Country
    admin_area = db.Column(db.String(20))  # State / Province / Region / Oblast / etc.
    sub_admin_area = db.Column(db.String(20))
    locality = db.Column(db.String(50))  # City / Town
    postal_code = db.Column(db.String(20))
    thoroughfare = db.Column(db.String(25))  # Street Address
    premise = db.Column(db.String(50))  # Apartment / Suite / etc.
    publisher = db.relationship('Publisher', backref='address', lazy=True)
