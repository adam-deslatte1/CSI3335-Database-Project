from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, User, TriviaQuestion, UserTriviaHistory, UserLifeline
import json
import random

trivia = Blueprint('trivia', __name__)

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

@trivia.route('/trivia')
def play_trivia():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
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
        flash('No questions available for this level', 'error')
        return redirect(url_for('main.dashboard'))
    
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

@trivia.route('/trivia/fifty-fifty', methods=['POST'])
def fifty_fifty():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    data = request.get_json()
    question = TriviaQuestion.query.get_or_404(data['question_id'])
    
    # Get all options except the correct answer
    wrong_options = [opt for opt in question.options if opt != question.correct_answer]
    # Randomly select two wrong options to eliminate
    eliminated = random.sample(wrong_options, 2)
    
    return jsonify({'eliminated_options': eliminated})

@trivia.route('/trivia/phone-friend', methods=['POST'])
def phone_friend():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    data = request.get_json()
    question = TriviaQuestion.query.get_or_404(data['question_id'])
    
    # Simulate friend's advice (70% chance of being correct)
    if random.random() < 0.7:
        advice = f"I'm pretty sure it's {question.correct_answer}"
    else:
        wrong_options = [opt for opt in question.options if opt != question.correct_answer]
        advice = f"I think it might be {random.choice(wrong_options)}"
    
    return jsonify({'advice': advice})

@trivia.route('/trivia/ask-audience', methods=['POST'])
def ask_audience():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
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

@trivia.route('/trivia/walk-away', methods=['POST'])
def walk_away():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    current_prize = session.get('current_prize', 0)
    session['game_over'] = True
    
    return jsonify({'prize_money': current_prize})

@trivia.route('/trivia/answer', methods=['POST'])
def trivia_answer():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
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