from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# Reflect Lahman tables - these are read-only reflections of the existing tables
class Team(db.Model):
    __tablename__ = 'teams'
    __table_args__ = {
        'extend_existing': True,
        'mysql_charset': 'utf8mb3',
        'mysql_collate': 'utf8mb3_general_ci'
    }
    # These columns should match exactly what's in the Lahman database
    # We're not creating a new table, just reflecting the existing one
    teams_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teamID = db.Column(db.CHAR(3), nullable=False)
    yearID = db.Column(db.SmallInteger, nullable=False)
    lgID = db.Column(db.CHAR(2))
    divID = db.Column(db.CHAR(1))
    franchID = db.Column(db.String(3))
    team_name = db.Column(db.String(50))

class Person(db.Model):
    __tablename__ = 'people'
    __table_args__ = {
        'extend_existing': True,
        'mysql_charset': 'utf8mb3',
        'mysql_collate': 'utf8mb3_general_ci'
    }
    # These columns should match exactly what's in the Lahman database
    # We're not creating a new table, just reflecting the existing one
    playerID = db.Column(db.String(9), primary_key=True)
    nameFirst = db.Column(db.String(255))
    nameLast = db.Column(db.String(255))

# Application-specific tables
class User(db.Model, UserMixin):
    __tablename__ = 'app_users'
    __table_args__ = {
        'mysql_charset': 'utf8mb3',
        'mysql_collate': 'utf8mb3_general_ci'
    }
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

class NoHitter(db.Model):
    __tablename__ = 'no_hitters'
    __table_args__ = {
        'mysql_charset': 'utf8mb3',
        'mysql_collate': 'utf8mb3_general_ci'
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    team = db.Column(db.String(100), nullable=False)
    opponent = db.Column(db.String(100), nullable=False)
    score = db.Column(db.String(20), nullable=False)
    is_perfect_game = db.Column(db.Boolean, default=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.teams_ID', name='fk_no_hitter_team_id'))
    opponent_team_id = db.Column(db.Integer, db.ForeignKey('teams.teams_ID', name='fk_no_hitter_opponent_team_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pitchers = db.relationship('Person', secondary='no_hitter_pitchers', backref='no_hitters')

class NoHitterPitcher(db.Model):
    __tablename__ = 'no_hitter_pitchers'
    __table_args__ = {
        'mysql_charset': 'utf8mb3',
        'mysql_collate': 'utf8mb3_general_ci'
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    no_hitter_id = db.Column(db.Integer, db.ForeignKey('no_hitters.id', name='fk_no_hitter_id'))
    player_id = db.Column(db.String(9), db.ForeignKey('people.playerID', name='fk_pitcher_id'))
    is_primary = db.Column(db.Boolean, default=False)  # True for the main pitcher
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserTriviaHistory(db.Model):
    __tablename__ = 'app_trivia_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('app_trivia_questions.id'), nullable=False)
    user_answer = db.Column(db.String(255))
    is_correct = db.Column(db.Boolean)
    points_earned = db.Column(db.Integer)
    lifelines_used = db.Column(db.JSON)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

class TriviaQuestion(db.Model):
    __tablename__ = 'app_trivia_questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    options = db.Column(db.JSON)
    level = db.Column(db.Integer)
    prize_money = db.Column(db.Integer)
    is_safe_haven = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('app_users.id'))
    is_active = db.Column(db.Boolean, default=True)

class UserLifeline(db.Model):
    __tablename__ = 'app_lifelines'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_users.id'), nullable=False)
    lifeline_type = db.Column(db.String(20))
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Remove Team, Player, Division, and DivisionHistory models as we'll use Lahman tables instead

class HigherLowerLeaderboard(db.Model):
    __tablename__ = 'higher_lower_leaderboard'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_users.id'))
    streak = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
