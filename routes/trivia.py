from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from ..models import db, User, TriviaQuestion, UserTriviaHistory, UserLifeline
from flask_login import login_required, current_user
import json
import random
from sqlalchemy import text
from ..fetch import FETCHER_MAP
import re

trivia = Blueprint('trivia', __name__)

# Prize money levels (in dollars)
PRIZE_MONEY = {
    1: 500,
    2: 1200,
    3: 2750,
    4: 6500,   # Safe haven
    5: 15000,
    6: 35000,
    7: 85000,  # Safe haven
    8: 200000,
    9: 1000000  # Safe haven
}
SAFE_HAVENS = [4, 7, 9]

FETCHERS_WITH_DIFFICULTY = {
    "fetch_year", "fetch_year_with_ws", "fetch_year_recent"
}

def run_sql(sql):
    result = db.session.execute(text(sql))
    return [row[0] for row in result.fetchall()]

@trivia.route('/trivia', methods=['GET', 'POST'])
def play_trivia():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Initialize/reset game state if starting new game
    if 'current_level' not in session or session.get('game_over'):
        session['current_level'] = 1
        session['current_prize'] = 0
        session['game_over'] = False
        session['used_lifelines'] = []
        session['fifty_fifty_eliminated'] = []

    current_level = session.get('current_level', 1)
    show_result = False
    is_correct = None
    correct_answer = None
    user_answer = None
    new_prize = session.get('current_prize', 0)
    game_over = session.get('game_over', False)
    used_lifelines = session.get('used_lifelines', [])
    fifty_fifty_eliminated = session.get('fifty_fifty_eliminated', [])

    if request.method == 'POST':
        # Handle 50:50 lifeline
        if request.form.get('lifeline') == '5050' and '5050' not in used_lifelines:
            # Use current question/options from session
            options = session.get('current_options')
            correct_answer = session.get('current_correct_answer')
            if not options or not correct_answer:
                flash('No current question available for 50:50.', 'error')
                return redirect(url_for('main.dashboard'))
            # Eliminate two wrong answers
            wrong_only = [opt for opt in options if opt != correct_answer]
            eliminated = random.sample(wrong_only, min(2, len(wrong_only)))
            session['fifty_fifty_eliminated'] = eliminated
            used_lifelines.append('5050')
            session['used_lifelines'] = used_lifelines
            question_id = session.get('current_question_id')
            question = TriviaQuestion.query.get(question_id) if question_id else None
            question_text = session.get('current_question_text')
            return render_template(
                'trivia.html',
                question_text=question_text,
                question=question,
                options=options,
                correct_answer=correct_answer,
                current_prize=session.get('current_prize', 0),
                used_lifelines=used_lifelines,
                fifty_fifty_eliminated=eliminated,
                phone_friend_suggestion=session.get('phone_friend_suggestion', None),
                current_level=current_level,
                PRIZE_MONEY=PRIZE_MONEY,
                SAFE_HAVENS=SAFE_HAVENS,
                show_result=False,
                game_over=False
            )
        # Handle Phone a Friend lifeline
        if request.form.get('lifeline') == 'phone' and 'phone' not in used_lifelines:
            # Use current question/options from session
            question_id = session.get('current_question_id')
            options = session.get('current_options')
            correct_answer = session.get('current_correct_answer')
            if not question_id or not options or not correct_answer:
                flash('No current question available for Phone a Friend.', 'error')
                return redirect(url_for('main.dashboard'))
            import random as pyrandom
            if pyrandom.random() < 0.75:
                suggestion = f"I'm pretty sure it's {correct_answer}"
            else:
                wrong_only = [opt for opt in options if opt != correct_answer]
                wrong_answer = pyrandom.choice(wrong_only) if wrong_only else correct_answer
                suggestion = f"I think it might be {wrong_answer}"
            session['phone_friend_suggestion'] = suggestion
            used_lifelines.append('phone')
            session['used_lifelines'] = used_lifelines
            # Re-render the current question
            question = TriviaQuestion.query.get(question_id)
            question_text = session.get('current_question_text')
            return render_template(
                'trivia.html',
                question_text=question_text,
                question=question,
                options=options,
                correct_answer=correct_answer,
                current_prize=session.get('current_prize', 0),
                used_lifelines=used_lifelines,
                fifty_fifty_eliminated=session.get('fifty_fifty_eliminated', []),
                phone_friend_suggestion=suggestion,
                current_level=current_level,
                PRIZE_MONEY=PRIZE_MONEY,
                SAFE_HAVENS=SAFE_HAVENS,
                show_result=False,
                game_over=False
            )
        # If this is a regular answer submission, clear the phone_friend_suggestion
        if request.form.get('answer'):
            session['phone_friend_suggestion'] = None
        user_answer = request.form.get('answer')
        correct_answer = request.form.get('correct_answer')
        is_correct = user_answer and correct_answer and user_answer.strip().lower() == correct_answer.strip().lower()
        show_result = True

        if is_correct:
            new_prize = PRIZE_MONEY[current_level]
            session['current_prize'] = new_prize
            if current_level < 9:
                session['current_level'] = current_level + 1
            else:
                session['game_over'] = True
                user = User.query.get(session['user_id'])
                user.score = max(user.score, new_prize)
                db.session.commit()
        else:
            if current_level in SAFE_HAVENS:
                new_prize = PRIZE_MONEY[current_level]
            else:
                last_safe_haven = max([h for h in SAFE_HAVENS if h < current_level], default=0)
                new_prize = PRIZE_MONEY[last_safe_haven] if last_safe_haven > 0 else 0
            session['game_over'] = True
            user = User.query.get(session['user_id'])
            user.score = max(user.score, new_prize)
            db.session.commit()
        game_over = session.get('game_over', False)
        generate_new_question = False  # Always show result after answer
    else:
        generate_new_question = True if request.method == 'GET' else False

    # Only get a new question on GET or after a correct answer
    if generate_new_question:
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                if current_level <= 4:
                    difficulty = 'easy'
                elif current_level <= 7:
                    difficulty = 'medium'
                else:
                    difficulty = 'hard'

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

                def extract_vars(s):
                    return set(re.findall(r'\{(\w+)\}', s or ''))
                needed_vars = set()
                needed_vars |= extract_vars(question.template)
                needed_vars |= extract_vars(question.sql_template)
                needed_vars |= extract_vars(question.wrong_sql_template)

                template_vars = {}
                for fetcher_name in fetchers:
                    fetcher_func = FETCHER_MAP.get(fetcher_name)
                    if fetcher_func is None:
                        raise Exception(f'Unknown fetcher: {fetcher_name}')
                    if fetcher_name in FETCHERS_WITH_DIFFICULTY:
                        fetch_value = fetcher_func(question.difficulty)
                    else:
                        fetch_value = fetcher_func()
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
                        key = fetcher_name.replace('fetch_', '')
                        template_vars[key] = fetch_value

                missing_vars = [v for v in needed_vars if v not in template_vars or template_vars[v] is None]
                if missing_vars:
                    raise Exception(f'Could not generate question due to missing variables: {missing_vars}')

                def sql_escape(val):
                    if isinstance(val, str):
                        return val.replace("'", "''")
                    return val
                escaped_template_vars = {k: sql_escape(v) for k, v in template_vars.items()}

                question_text = question.template.format(**template_vars)
                correct_sql = question.sql_template.format(**escaped_template_vars)
                wrong_sql = question.wrong_sql_template.format(**escaped_template_vars)

                correct_answers = run_sql(correct_sql)
                wrong_answers = run_sql(wrong_sql)

                if not correct_answers:
                    raise Exception('No correct answer found')
                correct_answer = correct_answers[0]
                options = [correct_answer] + wrong_answers[:3]
                random.shuffle(options)

                # Store current question state in session for lifelines
                session['current_question_id'] = question.id
                session['current_options'] = options
                session['current_correct_answer'] = correct_answer
                session['current_question_text'] = question_text
                session['fifty_fifty_eliminated'] = []  # Reset 50:50 on new question

                return render_template(
                    'trivia.html',
                    question_text=question_text,
                    question=question,
                    options=options,
                    correct_answer=correct_answer,
                    current_prize=session.get('current_prize', 0),
                    used_lifelines=used_lifelines,
                    fifty_fifty_eliminated=session.get('fifty_fifty_eliminated', []),
                    phone_friend_suggestion=session.get('phone_friend_suggestion', None),
                    current_level=current_level,
                    PRIZE_MONEY=PRIZE_MONEY,
                    SAFE_HAVENS=SAFE_HAVENS,
                    show_result=False,
                    game_over=False
                )
            except Exception as e:
                if attempt == max_attempts - 1:
                    flash(f'Could not generate a valid question. Please try again later. (Error: {e})', 'error')
                    return redirect(url_for('main.dashboard'))
                continue

    # If showing result, render with result info and no new question
    if not generate_new_question:
        # Use current question/options from session for result display
        question_id = session.get('current_question_id')
        question = TriviaQuestion.query.get(question_id) if question_id else None
        options = session.get('current_options')
        question_text = session.get('current_question_text')
        return render_template(
            'trivia.html',
            question_text=question_text,
            question=question,
            options=options,
            correct_answer=correct_answer,
            user_answer=user_answer,
            is_correct=is_correct,
            current_prize=new_prize,
            used_lifelines=used_lifelines,
            fifty_fifty_eliminated=session.get('fifty_fifty_eliminated', []),
            phone_friend_suggestion=session.get('phone_friend_suggestion', None),
            current_level=current_level,
            PRIZE_MONEY=PRIZE_MONEY,
            SAFE_HAVENS=SAFE_HAVENS,
            show_result=True,
            game_over=game_over
        )

@trivia.route('/trivia/fifty-fifty', methods=['POST'])
def fifty_fifty():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    # Use session for current options and correct answer
    options = session.get('current_options')
    correct_answer = session.get('current_correct_answer')
    if not options or not correct_answer:
        return jsonify({'error': 'No current question available.'}), 400
    wrong_options = [opt for opt in options if opt != correct_answer]
    eliminated = random.sample(wrong_options, min(2, len(wrong_options)))
    session['fifty_fifty_eliminated'] = eliminated
    return jsonify({'eliminated_options': eliminated})

@trivia.route('/trivia/phone-friend', methods=['POST'])
def phone_friend():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    options = session.get('current_options')
    correct_answer = session.get('current_correct_answer')
    if not options or not correct_answer:
        return jsonify({'error': 'No current question available.'}), 400
    if random.random() < 0.75:  # 75% chance of being correct
        advice = f"I'm pretty sure it's {correct_answer}"
    else:
        wrong_options = [opt for opt in options if opt != correct_answer]
        advice = f"I think it might be {random.choice(wrong_options)}" if wrong_options else f"I'm not sure."
    session['phone_friend_suggestion'] = advice
    return jsonify({'advice': advice})

@trivia.route('/trivia/ask-audience', methods=['POST'])
def ask_audience():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    options = session.get('current_options')
    correct_answer = session.get('current_correct_answer')
    if not options or not correct_answer:
        return jsonify({'error': 'No current question available.'}), 400
    correct_percentage = random.randint(40, 70)
    remaining = 100 - correct_percentage
    wrong_options = [opt for opt in options if opt != correct_answer]
    results = {correct_answer: correct_percentage}
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