from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets

db = SQLAlchemy()
login_manager = LoginManager()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/transport_company_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BCRYPT_LOG_ROUNDS'] = 12
    app.secret_key = secrets.token_hex(16)
    db.init_app(app)
    login_manager.init_app(app)
    return app
