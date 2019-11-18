from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, Email, ValidationError
from seshat.models import User


class BookForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()], render_kw={'autofocus': True})
    author = StringField('Author', validators=[InputRequired()])
    submit = SubmitField('Add Book')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[InputRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

    def validate(self):
        if not super(SearchForm, self).validate():
            return False
        if not self.title.data or self.author.data:
            msg = 'At least one of title or author must be filled in.'
            self.title.errors.append(msg)
            self.author.errors.append(msg)
            return False
        return True


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={'autofocus': True})
    email = StringField('email', validators=[InputRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('An account with this email already exists.')
