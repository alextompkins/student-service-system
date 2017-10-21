import os
basedir = os.path.abspath(os.path.dirname(__file__)) + '\\serviceapp'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'service.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
