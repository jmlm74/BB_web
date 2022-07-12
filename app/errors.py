from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def my_403_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(401)
def my_401_error(error):
    return render_template('errors/401.html'), 401
