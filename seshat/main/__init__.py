from flask import Blueprint

bp = Blueprint('main', __name__)

from seshat.main import routes
