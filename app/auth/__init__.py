from flask import Blueprint
bp = Blueprint('auth', __name__)

from dotenv import load_dotenv
load_dotenv()

from app.auth import routes

