import os
import unittest

from config import basedir
from seshat import app, db
from seshat.models import User


class TestCase(unittest.TestCase):

    def SetUp(self):
        app.config['TESTING'] = True
        # app.config['DEBUG'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def TearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_registration(self):
        pass
