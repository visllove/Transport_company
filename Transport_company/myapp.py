from flask import Flask
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/transport_company_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = secrets.token_hex(16)
    db.init_app(app)

    # login_manager = LoginManager(app)

    return app