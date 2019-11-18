from flask import render_template
from seshat import db
from seshat.errors import bp


@bp.app_errorhandler(401)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/401.html'), 500


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
