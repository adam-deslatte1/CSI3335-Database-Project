from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..models import db, Person, HigherLowerLeaderboard
from sqlalchemy.sql import func
import random

game = Blueprint('higher_lower', __name__)

ALL_STATS = [
    # Batting
    ('batting', 'b_HR', 'Home Runs', False, False),
    ('batting', 'b_H', 'Hits', False, False),
    ('batting', 'b_RBI', 'Runs Batted In', False, False),
    ('batting', 'b_SB', 'Stolen Bases', False, False),
    ('batting', 'b_BB', 'Walks', False, False),
    ('batting', 'b_SO', 'Strikeouts', False, False),
    ('batting', 'b_R', 'Runs', False, False),
    ('batting', 'b_2B', 'Doubles', False, False),
    ('batting', 'b_3B', 'Triples', False, False),
    ('batting', 'b_G', 'Games Played', False, False),
    ('batting', 'b_AB', 'At Bats', False, False),
    # Pitching
    ('pitching', 'p_W', 'Wins', False, False),
    ('pitching', 'p_L', 'Losses', False, False),
    ('pitching', 'p_SV', 'Saves', False, False),
    ('pitching', 'p_SO', 'Strikeouts (Pitching)', False, False),
    ('pitching', 'p_ERA', 'Earned Run Average', True, False),
    ('pitching', 'p_G', 'Games Pitched', False, False),
    ('pitching', 'p_SHO', 'Shutouts', False, False),
    ('pitching', 'p_CG', 'Complete Games', False, False),
    ('pitching', 'p_IPOuts', 'Innings Pitched (Outs)', False, False),
    ('pitching', 'p_H', 'Hits Allowed', False, False),
    ('pitching', 'p_BB', 'Walks Allowed', False, False),
    ('pitching', 'p_HR', 'Home Runs Allowed', False, False),
    # Fielding
    ('fielding', 'f_G', 'Games (Fielding)', False, False),
    ('fielding', 'f_GS', 'Games Started (Fielding)', False, False),
    ('fielding', 'f_PO', 'Putouts', False, False),
    ('fielding', 'f_A', 'Assists', False, False),
    ('fielding', 'f_E', 'Errors', False, False),
    ('fielding', 'f_DP', 'Double Plays', False, False),
    # Salaries
    ('salaries', 'salary', 'Career Salary', True, False),
    # Awards
    ('awards', 'awardID', 'Total Awards Won', False, True),
]

from sqlalchemy import text

def get_random_player(exclude_player_id=None):
    # Query for a random player
    query = """
        SELECT p.playerID, p.nameFirst, p.nameLast
        FROM people p
        JOIN batting b ON p.playerID = b.playerID
    """
    if exclude_player_id:
        query += " WHERE p.playerID != :exclude_player_id"
    query += " GROUP BY p.playerID ORDER BY RAND() LIMIT 1"
    result = db.session.execute(text(query), {'exclude_player_id': exclude_player_id} if exclude_player_id else {}).first()
    if result:
        return {
            'playerID': result[0],
            'nameFirst': result[1],
            'nameLast': result[2],
        }
    return None

def get_player_stat(playerID, table, col, is_float=False, is_count=False):
    if table == 'batting':
        query = f"SELECT SUM({col}) FROM batting WHERE playerID = :playerID"
    elif table == 'pitching':
        query = f"SELECT SUM({col}) FROM pitching WHERE playerID = :playerID"
    elif table == 'fielding':
        query = f"SELECT SUM({col}) FROM fielding WHERE playerID = :playerID"
    elif table == 'salaries':
        query = f"SELECT SUM({col}) FROM salaries WHERE playerID = :playerID"
    elif table == 'awards' and is_count:
        query = f"SELECT COUNT(*) FROM awards WHERE playerID = :playerID"
    else:
        return 0
    result = db.session.execute(text(query), {'playerID': playerID}).first()
    if is_float:
        return float(result[0]) if result and result[0] is not None else 0.0
    return int(result[0]) if result and result[0] is not None else 0

@game.route('/higher_lower', methods=['GET', 'POST'])
@login_required
def higher_lower():
    if 'hl_streak' not in session:
        session['hl_streak'] = 0
    if request.method == 'POST':
        # Handle guess
        if 'guess' in request.form:
            left = session.get('hl_left')
            right = session.get('hl_right')
            stat_info = session.get('hl_stat_info')
            guess = request.form.get('guess')
            if not left or not right or not stat_info or not guess:
                flash('Game state error. Please try again.', 'danger')
                return redirect(url_for('higher_lower.higher_lower'))
            table, col, label, is_float, is_count = stat_info
            left_val = left['stat']
            right_val = right['stat']
            correct = (
                (guess == 'higher' and right_val > left_val) or
                (guess == 'lower' and right_val < left_val) or
                (right_val == left_val)
            )
            session['hl_reveal'] = True
            session['hl_last_correct'] = correct
            if correct:
                session['hl_streak'] += 1
            else:
                # Save to leaderboard if highest streak
                if current_user.is_authenticated:
                    prev_best = HigherLowerLeaderboard.query.filter_by(user_id=current_user.id).order_by(HigherLowerLeaderboard.streak.desc()).first()
                    if not prev_best or session['hl_streak'] > prev_best.streak:
                        entry = HigherLowerLeaderboard(user_id=current_user.id, streak=session['hl_streak'])
                        db.session.add(entry)
                        db.session.commit()
                # Do NOT set hl_game_over here; wait for 'continue' button
            return redirect(url_for('higher_lower.higher_lower'))
        
        # Handle next button
        elif 'next' in request.form:
            if session.get('hl_last_correct'):
                # Pick a new stat to compare
                stat_info = random.choice(ALL_STATS)
                table, col, label, is_float, is_count = stat_info
                # Move right to left, recalculate stat for new stat_info
                left_player = session['hl_right']
                left_player['stat'] = get_player_stat(left_player['playerID'], table, col, is_float, is_count)
                session['hl_left'] = left_player
                session['hl_stat_info'] = stat_info
                # Pick a new right player and calculate their stat for the same stat_info
                new_right = get_random_player(exclude_player_id=left_player['playerID'])
                new_right['stat'] = get_player_stat(new_right['playerID'], table, col, is_float, is_count)
                session['hl_right'] = new_right
                session['hl_reveal'] = False
                session['hl_last_correct'] = None
            return redirect(url_for('higher_lower.higher_lower'))

        # Handle continue button (after incorrect guess)
        elif 'continue' in request.form:
            session['hl_game_over'] = True
            return redirect(url_for('higher_lower.higher_lower'))

    # GET: start or continue game
    if 'hl_left' not in session or 'hl_right' not in session:
        # Pick a stat to compare
        stat_info = random.choice(ALL_STATS)
        table, col, label, is_float, is_count = stat_info
        left = get_random_player()
        left['stat'] = get_player_stat(left['playerID'], table, col, is_float, is_count)
        right = get_random_player(exclude_player_id=left['playerID'])
        right['stat'] = get_player_stat(right['playerID'], table, col, is_float, is_count)
        session['hl_left'] = left
        session['hl_right'] = right
        session['hl_stat_info'] = stat_info
        session['hl_streak'] = 0
        session.pop('hl_game_over', None)
        session['hl_last_correct'] = None
        session['hl_reveal'] = False  # Only reset here!

    # Do NOT reset session['hl_reveal'] or session['hl_last_correct'] here

    return render_template('higher_lower.html',
        left=session['hl_left'],
        right=session['hl_right'],
        stat_label=session['hl_stat_info'][2],
        streak=session['hl_streak'],
        reveal=session.get('hl_reveal', False),
        last_correct=session.get('hl_last_correct', None),
        game_over=session.get('hl_game_over', False)
    )

@game.route('/higher_lower/retry')
@login_required
def higher_lower_retry():
    # Reset game state
    session.pop('hl_left', None)
    session.pop('hl_right', None)
    session.pop('hl_stat_info', None)
    session['hl_streak'] = 0
    session.pop('hl_game_over', None)
    session['hl_reveal'] = False
    session['hl_last_correct'] = None
    return redirect(url_for('higher_lower.higher_lower'))

@game.route('/higher_lower/leaderboard')
@login_required
def higher_lower_leaderboard():
    top10 = HigherLowerLeaderboard.query.order_by(HigherLowerLeaderboard.streak.desc()).limit(10).all()
    return render_template('higher_lower_leaderboard.html', top10=top10) 