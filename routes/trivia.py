from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, User, TriviaQuestion, UserTriviaHistory, UserLifeline
import json
import random
from sqlalchemy import text
from fetch import FETCHER_MAP
import re

trivia = Blueprint('trivia', __name__)

# Prize money levels (in dollars)
PRIZE_MONEY = {
    1: 100,
    2: 200,
    3: 300,
    4: 500,   # Safe haven
    5: 1000,
    6: 2000,
    7: 4000,  # Safe haven
    8: 8000,
    9: 16000  # Safe haven
}
SAFE_HAVENS = [4, 7, 9]

FETCHERS_WITH_DIFFICULTY = {
    "fetch_year", "fetch_year_with_ws", "fetch_year_recent"
}

def run_sql(sql):
    result = db.session.execute(text(sql))
    return [row[0] for row in result.fetchall()]

@trivia.route('/trivia')
def play_trivia():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Initialize/reset game state if starting new game
    if 'current_level' not in session or session.get('game_over'):
        session['current_level'] = 1
        session['current_prize'] = 0
        session['game_over'] = False

    current_level = session.get('current_level', 1)
    if current_level <= 4:
        difficulty = 'easy'
    elif current_level <= 7:
        difficulty = 'medium'
    else:
        difficulty = 'hard'

    # Get a random question for the correct difficulty
    question = TriviaQuestion.query.filter(
        TriviaQuestion.fetchers != None,
        TriviaQuestion.fetchers != '',
        TriviaQuestion.fetchers != '[]',
        TriviaQuestion.difficulty == difficulty
    ).order_by(db.func.rand()).first()
    if not question:
        flash('No questions available', 'error')
        return redirect(url_for('main.dashboard'))

    fetchers = json.loads(question.fetchers)
    if not fetchers:
        flash('No fetcher defined for this question.', 'error')
        return redirect(url_for('main.dashboard'))

    # --- Robustly extract all template variables ---
    def extract_vars(s):
        return set(re.findall(r'\{(\w+)\}', s or ''))
    needed_vars = set()
    needed_vars |= extract_vars(question.template)
    needed_vars |= extract_vars(question.sql_template)
    needed_vars |= extract_vars(question.wrong_sql_template)

    template_vars = {}
    # Support multiple fetchers and assign to correct variables
    for fetcher_name in fetchers:
        fetcher_func = FETCHER_MAP.get(fetcher_name)
        if fetcher_func is None:
            flash(f'Unknown fetcher: {fetcher_name}', 'error')
            return redirect(url_for('main.dashboard'))
        # Pass difficulty if needed
        if fetcher_name in FETCHERS_WITH_DIFFICULTY:
            fetch_value = fetcher_func(question.difficulty)
        else:
            fetch_value = fetcher_func()
        # Assign fetch_value to the correct variable(s)
        # Map fetcher_name to variable name(s)
        if fetcher_name == 'fetch_team_name':
            template_vars['team_name'] = fetch_value
        elif fetcher_name == 'fetch_year' or fetcher_name == 'fetch_year_with_ws' or fetcher_name == 'fetch_year_recent':
            template_vars['year'] = fetch_value
        elif fetcher_name == 'fetch_hof_first_name':
            template_vars['nameFirst'] = fetch_value
        elif fetcher_name == 'fetch_hof_last_name':
            template_vars['nameLast'] = fetch_value
        elif fetcher_name == 'fetch_full_hof_name':
            if isinstance(fetch_value, tuple):
                template_vars['nameFirst'] = fetch_value[0]
                template_vars['nameLast'] = fetch_value[1]
        elif fetcher_name == 'fetch_team_city':
            template_vars['city'] = fetch_value
        elif fetcher_name == 'fetch_team_state' or fetcher_name == 'fetch_multi_team_state':
            template_vars['state'] = fetch_value
        elif fetcher_name == 'fetch_rank':
            template_vars['rank'] = fetch_value
        else:
            # Fallback: assign to variable named after fetcher
            key = fetcher_name.replace('fetch_', '')
            template_vars[key] = fetch_value

    # If any needed var is still missing, skip this question
    missing_vars = [v for v in needed_vars if v not in template_vars or template_vars[v] is None]
    if missing_vars:
        flash(f'Could not generate question due to missing variables: {missing_vars}', 'error')
        return redirect(url_for('main.dashboard'))

    # Escape all string values in template_vars for SQL
    def sql_escape(val):
        if isinstance(val, str):
            return val.replace("'", "''")
        return val
    escaped_template_vars = {k: sql_escape(v) for k, v in template_vars.items()}

    question_text = question.template.format(**template_vars)
    correct_sql = question.sql_template.format(**escaped_template_vars)
    wrong_sql = question.wrong_sql_template.format(**escaped_template_vars)

    print("Difficulty:", difficulty)
    print("Correct SQL:", correct_sql)

    correct_answers = run_sql(correct_sql)
    wrong_answers = run_sql(wrong_sql)

    # Pick one correct and up to 3 wrong answers
    if not correct_answers:
        flash('No correct answer found', 'error')
        return redirect(url_for('main.dashboard'))
    correct_answer = correct_answers[0]
    options = [correct_answer] + wrong_answers[:3]
    random.shuffle(options)

    return render_template(
        'trivia.html',
        question_text=question_text,
        options=options,
        correct_answer=correct_answer,
        current_prize=session.get('current_prize', 0),
        used_lifelines=[],
        current_level=current_level,
        PRIZE_MONEY=PRIZE_MONEY,
        SAFE_HAVENS=SAFE_HAVENS
    )

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

    user_answer = request.form.get('answer')
    correct_answer = request.form.get('correct_answer')

    is_correct = user_answer == correct_answer

    # Get current level and prize money
    current_level = session.get('current_level', 1)
    current_prize = session.get('current_prize', 0)

    if is_correct:
        # Update prize money
        new_prize = PRIZE_MONEY[current_level]
        session['current_prize'] = new_prize
        # If not at the last level, increment level
        if current_level < 9:
            session['current_level'] = current_level + 1
        else:
            session['game_over'] = True
    else:
        # If at a safe haven, keep the last safe haven prize
        if current_level in SAFE_HAVENS:
            new_prize = PRIZE_MONEY[current_level]
        else:
            # Find the last safe haven
            last_safe_haven = max([h for h in SAFE_HAVENS if h < current_level], default=0)
            new_prize = PRIZE_MONEY[last_safe_haven] if last_safe_haven > 0 else 0
        session['game_over'] = True

    # Record the answer (optional: you can add more fields as needed)
    # history = UserTriviaHistory(
    #     user_id=session['user_id'],
    #     question_id=question_id,  # Not available in this flow
    #     user_answer=user_answer,
    #     is_correct=is_correct,
    #     points_earned=new_prize,
    #     lifelines_used=json.dumps(session.get('used_lifelines', []))
    # )
    # db.session.add(history)
    # Update user score
    user = User.query.get(session['user_id'])
    user.score = max(user.score, new_prize)
    db.session.commit()

    return jsonify({
        'correct': is_correct,
        'prize_money': new_prize,
        'correct_answer': correct_answer,
        'current_level': session.get('current_level', 1)
    }) 