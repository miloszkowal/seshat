from flask import render_template
from seshat.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Seshat] Reset Your Password',
               sender='noreply@getseshat.app',
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
