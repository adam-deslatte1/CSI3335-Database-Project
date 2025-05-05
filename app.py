from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, User, NoHitter, NoHitterPitcher, DivisionHistory, UserTriviaHistory, TriviaQuestion, UserTeamSelection, UserLifeline
from werkzeug.security import generate_password_hash, check_password_hash
from csi3335s2025 import mysql
from datetime import datetime
import json
import random

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Configure SQLAlchemy for MariaDB with PyMySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql['user']}:{mysql['password']}@{mysql['location']}/{mysql['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Prize money levels (in dollars)
PRIZE_MONEY = {
    1: 100,
    2: 200,
    3: 300,
    4: 500,
    5: 1000,  # Safe haven
    6: 2000,
    7: 4000,
    8: 8000,
    9: 16000,
    10: 32000,  # Safe haven
    11: 64000,
    12: 125000,
    13: 250000,
    14: 500000,
    15: 1000000  # Safe haven
}

db.init_app(app)

# ✅ Create tables at app startup (Flask 2.3+ safe)
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123', salt_length=8),  # Using shorter salt
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        password = generate_password_hash(request.form['password'], salt_length=8)  # Using shorter salt
        new_user = User(username=username, password_hash=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            if user.is_banned:
                flash('Your account has been banned')
                return redirect(url_for('login'))
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
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

@app.route('/team/<int:team_id>/no-hitters')
def team_no_hitters(team_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Log the team selection
    selection = UserTeamSelection(
        user_id=session['user_id'],
        team_id=team_id
    )
    db.session.add(selection)
    db.session.commit()
    
    # Get no-hitters for the team
    no_hitters = NoHitter.query.filter(
        (NoHitter.home_team_id == team_id) | (NoHitter.away_team_id == team_id)
    ).all()
    
    return render_template('team_no_hitters.html', no_hitters=no_hitters)

@app.route('/trivia')
def trivia():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user's current level and prize money
    user = User.query.get(session['user_id'])
    current_level = session.get('current_level', 1)
    current_prize = session.get('current_prize', 0)
    
    # Get a question for the current level
    question = TriviaQuestion.query.filter_by(
        level=current_level,
        is_active=True
    ).order_by(db.func.rand()).first()
    
    if not question:
        flash('No questions available for this level')
        return redirect(url_for('dashboard'))
    
    # Get user's available lifelines
    lifelines = UserLifeline.query.filter_by(
        user_id=session['user_id'],
        is_used=False
    ).all()
    
    used_lifelines = [l.lifeline_type for l in lifelines if l.is_used]
    
    return render_template('trivia.html',
                         question=question,
                         current_prize=current_prize,
                         used_lifelines=used_lifelines)

@app.route('/trivia/fifty-fifty', methods=['POST'])
def fifty_fifty():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    data = request.get_json()
    question = TriviaQuestion.query.get_or_404(data['question_id'])
    
    # Get all options except the correct answer
    wrong_options = [opt for opt in question.options if opt != question.correct_answer]
    # Randomly select two wrong options to eliminate
    eliminated = random.sample(wrong_options, 2)
    
    return jsonify({'eliminated_options': eliminated})

@app.route('/trivia/phone-friend', methods=['POST'])
def phone_friend():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    data = request.get_json()
    question = TriviaQuestion.query.get_or_404(data['question_id'])
    
    # Simulate friend's advice (70% chance of being correct)
    if random.random() < 0.7:
        advice = f"I'm pretty sure it's {question.correct_answer}"
    else:
        wrong_options = [opt for opt in question.options if opt != question.correct_answer]
        advice = f"I think it might be {random.choice(wrong_options)}"
    
    return jsonify({'advice': advice})

@app.route('/trivia/ask-audience', methods=['POST'])
def ask_audience():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    data = request.get_json()
    question = TriviaQuestion.query.get_or_404(data['question_id'])
    
    # Simulate audience results
    # Give higher percentage to correct answer
    correct_percentage = random.randint(40, 70)
    remaining = 100 - correct_percentage
    wrong_options = [opt for opt in question.options if opt != question.correct_answer]
    
    results = {
        question.correct_answer: correct_percentage
    }
    
    # Distribute remaining percentage among wrong options
    for i, option in enumerate(wrong_options):
        if i == len(wrong_options) - 1:
            results[option] = remaining
        else:
            percentage = random.randint(5, remaining - (len(wrong_options) - i - 1) * 5)
            results[option] = percentage
            remaining -= percentage
    
    return jsonify({'results': results})

@app.route('/trivia/walk-away', methods=['POST'])
def walk_away():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_prize = session.get('current_prize', 0)
    session['game_over'] = True
    
    return jsonify({'prize_money': current_prize})

@app.route('/trivia/answer', methods=['POST'])
def trivia_answer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    question_id = request.form.get('question_id')
    user_answer = request.form.get('answer')
    
    question = TriviaQuestion.query.get_or_404(question_id)
    is_correct = user_answer == question.correct_answer
    
    # Get current level and prize money
    current_level = session.get('current_level', 1)
    current_prize = session.get('current_prize', 0)
    
    if is_correct:
        # Update prize money
        new_prize = PRIZE_MONEY[current_level]
        session['current_prize'] = new_prize
        
        # If not at the last level, increment level
        if current_level < 15:
            session['current_level'] = current_level + 1
        else:
            session['game_over'] = True
    else:
        # If at a safe haven, keep the last safe haven prize
        if current_level in [5, 10, 15]:
            new_prize = PRIZE_MONEY[current_level]
        else:
            # Find the last safe haven
            safe_havens = [5, 10, 15]
            last_safe_haven = max([h for h in safe_havens if h < current_level], default=0)
            new_prize = PRIZE_MONEY[last_safe_haven] if last_safe_haven > 0 else 0
        
        session['game_over'] = True
    
    # Record the answer
    history = UserTriviaHistory(
        user_id=session['user_id'],
        question_id=question_id,
        user_answer=user_answer,
        is_correct=is_correct,
        points_earned=new_prize,
        lifelines_used=json.dumps(session.get('used_lifelines', []))
    )
    db.session.add(history)
    
    # Update user score
    user = User.query.get(session['user_id'])
    user.score = max(user.score, new_prize)
    db.session.commit()
    
    return jsonify({
        'correct': is_correct,
        'prize_money': new_prize
    })

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/ban/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    user.is_banned = True
    db.session.commit()
    flash(f'User {user.username} has been banned')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/trivia', methods=['GET', 'POST'])
def manage_trivia():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
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
        flash('Question added successfully')
        return redirect(url_for('manage_trivia'))
    
    questions = TriviaQuestion.query.all()
    return render_template('manage_trivia.html', questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
