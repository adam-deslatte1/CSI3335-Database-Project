from flask import Blueprint, render_template, session, redirect, url_for
from models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=session['username'], user=user) 