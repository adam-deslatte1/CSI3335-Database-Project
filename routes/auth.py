from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        password = generate_password_hash(request.form['password'], salt_length=8)
        new_user = User(username=username, password_hash=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            if user.is_banned:
                flash('Your account has been banned', 'error')
                return redirect(url_for('auth.login'))
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index')) 