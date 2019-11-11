# configuration file for votr
import os

SECRET_KEY = 'development key'  # keep this key secret during production

DEBUG = True

#  DB_PATH = os.path.join(os.path.dirname(__file__), 'votr.db')
#  SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
SQLALCHEMY_DATABASE_URI = 'postgresql:///flask'
SQLALCHEMY_TRACK_MODIFICATIONS = False

#  CELERY_BROKER = 'amqp://guest@localhost//'
#  CELERY_RESULT_BACKEND = 'amqp://'

#  FLASK_ADMIN_SWATCH = 'default'
FLASK_ADMIN_SWATCH = 'cerulean'
