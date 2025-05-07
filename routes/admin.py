from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from models import db, User, TriviaQuestion
import json

admin = Blueprint('admin', __name__)

@admin.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@admin.route('/admin/ban/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(user_id)
    user.is_banned = True
    db.session.commit()
    flash(f'User {user.username} has been banned', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/admin/unban/<int:user_id>', methods=['POST'])
def unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    flash('User has been unbanned.', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin.route('/admin/trivia', methods=['GET', 'POST'])
def manage_trivia():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        question = TriviaQuestion(
            question_text=request.form['question'],
            correct_answer=request.form['correct_answer'],
            options=json.dumps(request.form.getlist('options')),
            difficulty=int(request.form['difficulty']),
            category=request.form['category'],
            created_by=session['user_id']
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully', 'success')
        return redirect(url_for('admin.manage_trivia'))
    
    questions = TriviaQuestion.query.all()
    return render_template('manage_trivia.html', questions=questions) 