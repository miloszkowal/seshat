from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError, Optional
from seshat.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={'autofocus': True})
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with this email already exists.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    login = SubmitField('Login')


class BookForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()], render_kw={'autofocus': True})
    author = StringField('Author', validators=[InputRequired()])
    submit = SubmitField('Add Book')


class SearchForm(FlaskForm):
    title = StringField('Title', validators=[Optional()], render_kw={'autofocus': True})
    author = StringField('Author', validators=[Optional()])
    submit = SubmitField('Search')

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
