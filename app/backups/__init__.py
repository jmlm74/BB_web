from flask import Blueprint


bp_backups = Blueprint('backups', __name__, static_folder='static', )

from dotenv import load_dotenv
load_dotenv()

from app.backups import routes
