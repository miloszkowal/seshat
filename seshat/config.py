class Config(object):
    SECRET_KEY = 'bcdca3e428f8eadc6d04761ceace3204'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ELASTICSEARCH_URL = 'http://localhost:9200'