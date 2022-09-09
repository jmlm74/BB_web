import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    debug = True
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or 1
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'jmlm74@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "boewippcwujthxpk"
    ADMINS = ['jmlm74@gmail.com']
    APPNAME = 'TAQ-BB'

    BORG_BINARY = '/usr/bin/borgmatic'
    BORG_RESTORE_PATH = '/home/partage/taq-partage/restore'