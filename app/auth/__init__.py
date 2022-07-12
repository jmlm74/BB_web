from flask import Blueprint
bp = Blueprint('auth', __name__, static_folder='static', template_folder='templates', )

from dotenv import load_dotenv
load_dotenv()

from app.auth import routes
