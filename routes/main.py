from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User, UserSelectionLog, NoHitter, Team
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

            # Query where team_id matches ANY of the IDs
            thrown_by = db.session.query(NoHitter).filter(NoHitter.team_id.in_(selected_team_ids)).all()
            thrown_against = db.session.query(NoHitter).filter(NoHitter.opponent_team_id.in_(selected_team_ids)).all()

            print(f"Thrown By: {thrown_by}")
            print(f"Thrown Against: {thrown_against}")

        else:
            flash('Please select a valid team.', 'danger')

    return render_template('team_nohitters.html', teams=teams, selected_team=selected_team, thrown_by=thrown_by, thrown_against=thrown_against)

