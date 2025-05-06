from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User, UserSelectionLog, NoHitter

main = Blueprint('main', __name__)

def get_all_team_names():
    teams = db.session.query(teams.team_name).distinct().all()
    opponents = db.session.query(NoHitter.opponent).distinct().all()
    all_teams = set([t[0] for t in teams] + [o[0] for o in opponents])
    return sorted(all_teams)

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
        
        if selected_team:
            # Log the selection
            log = UserSelectionLog(user_id=current_user.id, team_name=selected_team)
            db.session.add(log)
            db.session.commit()

            # Fetch no-hitters
            thrown_by = NoHitter.query.filter_by(team=selected_team).all()
            thrown_against = NoHitter.query.filter_by(opponent=selected_team).all()
        else:
            flash('Please select a valid team.', 'danger')

    return render_template('team_nohitters.html', teams=teams, selected_team=selected_team, thrown_by=thrown_by, thrown_against=thrown_against)