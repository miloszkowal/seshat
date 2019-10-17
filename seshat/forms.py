from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from seshat.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)])
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
    email = StringField('Email')
    password = PasswordField('Password')
    # remember = BooleanField()
    login = SubmitField('Login')


class BookForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    author = StringField('Author', validators=[InputRequired()])
    submit = SubmitField('Add Book')
