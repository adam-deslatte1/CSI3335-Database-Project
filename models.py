from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    trivia_history = db.relationship('UserTriviaHistory', backref='user', lazy=True)
    lifelines = db.relationship('UserLifeline', backref='user', lazy=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    founded_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    home_games = db.relationship('NoHitter', foreign_keys='NoHitter.home_team_id', backref='home_team', lazy=True)
    away_games = db.relationship('NoHitter', foreign_keys='NoHitter.away_team_id', backref='away_team', lazy=True)
    division_history = db.relationship('DivisionHistory', backref='team', lazy=True)
    user_selections = db.relationship('UserTeamSelection', backref='team', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    birth_city = db.Column(db.String(100))
    birth_state = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    no_hitters = db.relationship('NoHitterPitcher', backref='pitcher', lazy=True)

class Division(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    league = db.Column(db.String(50))  # 'AL' or 'NL'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    team_history = db.relationship('DivisionHistory', backref='division', lazy=True)

class NoHitter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    pitchers = db.Column(db.String(255), nullable=False)  # Comma-separated names
    team = db.Column(db.String(100), nullable=False)      # Team that threw the no-hitter
    opponent = db.Column(db.String(100), nullable=False)  # Opponent team
    score = db.Column(db.String(20), nullable=False)      # Score as string, e.g. '3-0'
    is_perfect_game = db.Column(db.Boolean, default=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))  # Main pitcher (first listed)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))      # Team that threw the no-hitter
    opponent_team_id = db.Column(db.Integer, db.ForeignKey('team.id'))  # Opponent team
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DivisionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    division_id = db.Column(db.Integer, db.ForeignKey('division.id'), nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserTriviaHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('trivia_question.id'), nullable=False)
    user_answer = db.Column(db.String(255))
    is_correct = db.Column(db.Boolean)
    points_earned = db.Column(db.Integer)
    lifelines_used = db.Column(db.JSON)  # Store which lifelines were used
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

class TriviaQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    options = db.Column(db.JSON)  # Store multiple choice options as JSON
    level = db.Column(db.Integer)  # 1-15 for Millionaire levels
    prize_money = db.Column(db.Integer)  # Prize money for this level
    is_safe_haven = db.Column(db.Boolean, default=False)  # True for levels 5, 10, 15
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)

class UserTeamSelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    selected_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserLifeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lifeline_type = db.Column(db.String(20))  # 'fifty_fifty', 'phone_friend', 'ask_audience'
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
