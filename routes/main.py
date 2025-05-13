from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User, UserSelectionLog, NoHitter, NoHitterPitcher, Person, Team, Division
from sqlalchemy import text

main = Blueprint('main', __name__)

def get_all_team_names():
    teams = db.session.query(Team.team_name).distinct().all()
    return sorted(set([t[0] for t in teams]))

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=session['username'], user=user)

@main.route('/team_nohitters', methods=['GET', 'POST'])
@login_required
def team_nohitters():
    teams = get_all_team_names()
    
    selected_team = None
    thrown_by = []
    thrown_against = []

    if request.method == 'POST':
        selected_team = request.form.get('team_name')

        # Get ALL team IDs with the selected name
        selected_team_ids = db.session.query(Team.teams_ID).filter_by(team_name=selected_team).all()
        selected_team_ids = [t[0] for t in selected_team_ids]

        print(f"Selected Team IDs: {selected_team_ids}")

        if selected_team_ids:
            # Log the selection
            if current_user.is_authenticated:
                log = UserSelectionLog(user_id=current_user.id, team_name=selected_team)
                db.session.add(log)
                db.session.commit()

            # Query no-hitters thrown BY the team
            nohitters_by = db.session.query(NoHitter).filter(NoHitter.team_id.in_(selected_team_ids)).all()
            # Query no-hitters thrown AGAINST the team
            nohitters_against = db.session.query(NoHitter).filter(NoHitter.opponent_team_id.in_(selected_team_ids)).all()

            # Process "thrown by"
            for nh in nohitters_by:
                pitchers = (
                    db.session.query(Person.nameFirst, Person.nameLast)
                    .join(NoHitterPitcher, NoHitterPitcher.player_id == Person.playerID)
                    .filter(NoHitterPitcher.no_hitter_id == nh.id)
                    .all()
                )
                pitcher_names = [f"{p[0]} {p[1]}" for p in pitchers]

                thrown_by.append({
                    'date': nh.date,
                    'pitchers': pitcher_names,
                    'opponent': nh.opponent,
                    'score': nh.score,
                    'is_perfect_game': nh.is_perfect_game
                })

            # Process "thrown against"
            for nh in nohitters_against:
                pitchers = (
                    db.session.query(Person.nameFirst, Person.nameLast)
                    .join(NoHitterPitcher, NoHitterPitcher.player_id == Person.playerID)
                    .filter(NoHitterPitcher.no_hitter_id == nh.id)
                    .all()
                )
                pitcher_names = [f"{p[0]} {p[1]}" for p in pitchers]

                thrown_against.append({
                    'date': nh.date,
                    'pitchers': pitcher_names,
                    'team': nh.team,
                    'score': nh.score,
                    'is_perfect_game': nh.is_perfect_game
                })

            print(f"Thrown By: {thrown_by}")
            print(f"Thrown Against: {thrown_against}")

        else:
            flash('Please select a valid team.', 'danger')

    return render_template(
        'team_nohitters.html',
        teams=teams,
        selected_team=selected_team,
        thrown_by=thrown_by,
        thrown_against=thrown_against
    )

@main.route('/team_divisions', methods=['GET'])
def team_divisions():
    # Get the selected year from the query parameters, default to current year if not specified
    selected_year = request.args.get('year')
    if selected_year:
        selected_year = int(selected_year)
    else:
        selected_year = 2024
    
    # Get all available years from the database
    years = db.session.query(Team.yearID).distinct().order_by(Team.yearID.desc()).all()
    years = [y[0] for y in years]
    
    # Query teams and their divisions for the selected year
    teams_by_division = {}
    if selected_year:
        # Get all teams for the selected year with their division information
        teams = db.session.query(
            Team.team_name,
            Team.lgID,
            Team.divID,
            Division.division_name
        ).outerjoin(
            Division,
            db.and_(
                Team.yearID == Division.yearID,
                Team.lgID == Division.lgID,
                Team.divID == Division.divID
            )
        ).filter(
            Team.yearID == selected_year
        ).order_by(
            Team.lgID,
            Team.divID,
            Team.team_name
        ).all()
        
        # Organize teams by league and division
        for team in teams:
            league = team.lgID
            division = team.division_name if team.division_name else 'No Division'
            
            if league not in teams_by_division:
                teams_by_division[league] = {}
            if division not in teams_by_division[league]:
                teams_by_division[league][division] = []
            
            teams_by_division[league][division].append(team.team_name)
    
    return render_template(
        'team_divisions.html',
        years=years,
        selected_year=selected_year,
        teams_by_division=teams_by_division
    )
