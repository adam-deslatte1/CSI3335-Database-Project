from flask import Blueprint, render_template, request, session, jsonify
from models import db, Person, GuessPlayerLeaderboard
from sqlalchemy import text, func
from flask_login import login_required, current_user
import random

guess_player = Blueprint('guess_player', __name__)

# Helper: get all possible player names for autocomplete
@guess_player.route('/guess-player/search')
def search_players():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])
    # Use SQL LIKE for case-insensitive partial match
    results = db.session.execute(text('''
        SELECT CONCAT(nameFirst, ' ', nameLast) AS full_name
        FROM people
        WHERE nameFirst IS NOT NULL AND nameLast IS NOT NULL
          AND CONCAT(nameFirst, ' ', nameLast) LIKE :pattern
        LIMIT 20
    '''), {'pattern': f'%{q}%'}).fetchall()
    names = [row[0] for row in results]
    return jsonify(names)

# Helper: get a random player (with team, division, position, status, HOF)
def get_random_player():
    player = db.session.execute(text('''
        SELECT p.playerID, p.nameFirst, p.nameLast, t.teamID, t.team_name, t.divID,
            COALESCE(
                (SELECT f2.position FROM fielding f2 WHERE f2.playerID = p.playerID AND f2.position IS NOT NULL LIMIT 1),
                (SELECT 'Pitch' FROM pitching pi WHERE pi.playerID = p.playerID LIMIT 1),
                (SELECT 'Bat' FROM batting b WHERE b.playerID = p.playerID LIMIT 1),
                'Unknown'
            ) AS position,
            CASE WHEN p.finalGameDate IS NULL OR YEAR(p.finalGameDate) IN (2022, 2023) THEN 'Current' ELSE 'Retired' END AS status,
            CASE WHEN h.inducted = 'Y' THEN 'Yes' ELSE 'No' END AS hof
        FROM people p
        JOIN appearances a ON p.playerID = a.playerID
        JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
        LEFT JOIN halloffame h ON p.playerID = h.playerID
        WHERE p.nameFirst IS NOT NULL AND p.nameLast IS NOT NULL
        ORDER BY RAND() LIMIT 1
    ''')).first()
    if not player:
        return None
    return {
        'playerID': player[0],
        'nameFirst': player[1],
        'nameLast': player[2],
        'teamID': player[3],
        'team_name': player[4],
        'division': player[5],
        'position': player[6],
        'status': player[7],
        'hof': player[8],
    }

# Start a new game
@guess_player.route('/guess-player/new', methods=['POST'])
def new_game():
    player = get_random_player()
    if not player:
        return jsonify({'error': 'Could not find a player.'}), 500
    session['gp_mystery'] = player
    session['gp_guesses'] = []
    session['gp_guess_count'] = 0
    return jsonify({'ok': True})

# Main game page
@guess_player.route('/guess-player')
def guess_player_page():
    return render_template('guess_player.html')

# Handle a guess
@guess_player.route('/guess-player/guess', methods=['POST'])
def guess_player_guess():
    guess_name = request.json.get('guess')
    mystery = session.get('gp_mystery')
    guesses = session.get('gp_guesses', [])
    guess_count = session.get('gp_guess_count', 0)
    if not mystery or guess_count >= 9:
        return jsonify({'error': 'No active game.'}), 400
    # Find guessed player
    result = db.session.execute(text('''
        SELECT p.playerID, p.nameFirst, p.nameLast, t.teamID, t.team_name, t.divID,
            COALESCE(
                (SELECT f2.position FROM fielding f2 WHERE f2.playerID = p.playerID AND f2.position IS NOT NULL LIMIT 1),
                (SELECT 'Pitch' FROM pitching pi WHERE pi.playerID = p.playerID LIMIT 1),
                (SELECT 'Bat' FROM batting b WHERE b.playerID = p.playerID LIMIT 1),
                'Unknown'
            ) AS position,
            CASE WHEN p.finalGameDate IS NULL OR YEAR(p.finalGameDate) IN (2022, 2023) THEN 'Current' ELSE 'Retired' END AS status,
            CASE WHEN h.inducted = 'Y' THEN 'Yes' ELSE 'No' END AS hof
        FROM people p
        JOIN appearances a ON p.playerID = a.playerID
        JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
        LEFT JOIN halloffame h ON p.playerID = h.playerID
        WHERE CONCAT(p.nameFirst, ' ', p.nameLast) = :guess
        LIMIT 1
    '''), {'guess': guess_name}).first()
    if not result:
        return jsonify({'error': 'Player not found.'}), 404
    guess = {
        'playerID': result[0],
        'nameFirst': result[1],
        'nameLast': result[2],
        'teamID': result[3],
        'team_name': result[4],
        'division': result[5],
        'position': result[6],
        'status': result[7],
        'hof': result[8],
    }
    # Compare attributes
    clues = {}
    for attr in ['team_name', 'division', 'position', 'status', 'hof']:
        clues[attr] = (guess[attr] == mystery[attr])
    guesses.append({'guess': guess, 'clues': clues})
    guess_count += 1
    session['gp_guesses'] = guesses
    session['gp_guess_count'] = guess_count
    win = all(clues.values())
    game_over = win or guess_count >= 9
    return jsonify({
        'clues': clues,
        'guess': guess,
        'guesses': guesses,
        'guess_count': guess_count,
        'win': win,
        'game_over': game_over,
        'mystery': mystery if game_over else None
    })

@guess_player.route('/guess-player/state')
def guess_player_state():
    guesses = session.get('gp_guesses', [])
    guess_count = session.get('gp_guess_count', 0)
    game_over = False
    win = False
    mystery = None
    if 'gp_mystery' in session:
        mystery = session['gp_mystery']
    if guess_count >= 9 or (guesses and all(g['clues'] and all(g['clues'].values()) for g in guesses)):
        game_over = True
        win = guesses and all(g['clues'] and all(g['clues'].values()) for g in guesses)
    return jsonify({
        'guesses': guesses,
        'guess_count': guess_count,
        'game_over': game_over,
        'win': win,
        'mystery': mystery if game_over else None
    }) 