from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash
from csi3335s2025 import mysql
from routes.auth import auth
from routes.main import main
from routes.trivia import trivia
from routes.admin import admin

from flask_wtf import CSRFProtect




app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Configure SQLAlchemy for MariaDB with PyMySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql['user']}:{mysql['password']}@{mysql['location']}/{mysql['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(trivia)
app.register_blueprint(admin)

db.init_app(app)

csrf = CSRFProtect(app)

# Create tables and admin user at app startup
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123', salt_length=8),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
