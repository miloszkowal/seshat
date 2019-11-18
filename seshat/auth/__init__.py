from flask import Blueprint

bp = Blueprint('auth', __name__)

from seshat.auth import routes
