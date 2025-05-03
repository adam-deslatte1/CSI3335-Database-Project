from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from csi3335s2025 import mysql

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Configure SQLAlchemy for MariaDB with PyMySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql['user']}:{mysql['password']}@{mysql['location']}/{mysql['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ✅ Create tables at app startup (Flask 2.3+ safe)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, password_hash=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            if user.is_banned:
                return "You are banned!"
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
        return "Invalid login"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
