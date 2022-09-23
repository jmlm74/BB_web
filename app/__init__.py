from functools import wraps
from flask import Flask, abort, flash, g
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_login import current_user
from flask_mail import Mail
import shutil
import os


app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

mail = Mail(app)

toolbar = DebugToolbarExtension(app)

bootstrap = Bootstrap5(app)

shutil.rmtree(app.config['TMPDIR'], ignore_errors=True, onerror=None)
if not os.path.isdir(app.config['TMPDIR']):
    os.mkdir(app.config['TMPDIR'])


def is_admin(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(current_user)
        try:
            if not current_user.is_admin:
                flash("You do not have permission to go there ! Admin only", "warning")
                abort(403)
        except AttributeError:
            flash("You do not have permission to go there ! Should login before", "warning")
            abort(401)
        return function(*args, **kwargs)
    return wrapper


from app.backups import bp_backups
app.register_blueprint(bp_backups, url_prefix='/backups')

from app.auth import bp as auth_bp, models
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.applogs import bp_applogs
app.register_blueprint(bp_applogs, url_prefix='/applogs')

from app import routes, errors
login_manager = LoginManager(app)
login_manager.login_view = 'auth/login'


@app.context_processor
def appinfo():
    return dict(appname=app.config.get('APPNAME'))

@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))

"""
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    # response.headers['Content-Security-Policy'] = "default-src 'self'; script-src *"
    return response

"""