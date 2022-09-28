from flask import Blueprint

bp_applogs = Blueprint('applogs', __name__, static_folder='static', template_folder='templates', )

from app.applogs import routes
