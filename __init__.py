from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from flask_login import LoginManager

# Import blueprints
from .routes.guess_player import guess_player
from .routes.auth import auth
from .routes.main import main
from .routes.trivia import trivia
from .routes.higher_lower import higher_lower
from .routes.admin import admin

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/baseball'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(trivia)
    app.register_blueprint(higher_lower)
    app.register_blueprint(admin)
    app.register_blueprint(guess_player)

    return app 