from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash
from csi3335s2025 import mysql
from routes.auth import auth
from routes.main import main
from routes.trivia import trivia
from routes.admin import admin
from routes.higher_lower import game as higher_lower_game

from flask_wtf import CSRFProtect
from flask_login import LoginManager




app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configure SQLAlchemy for MariaDB with MySQL Connector/Python
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{mysql['user']}:{mysql['password']}@{mysql['location']}/{mysql['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
if hasattr(db, 'init_app'):
    db.init_app(app)
csrf = CSRFProtect(app)

# Setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(trivia)
app.register_blueprint(admin)
app.register_blueprint(higher_lower_game)

# Create tables and admin user at app startup
with app.app_context():
    # Create all tables
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123', salt_length=8),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

@app.template_filter('format_number')
def format_number_filter(value):
    return "{:,}".format(value)

if __name__ == '__main__':
    app.run(debug=True)
