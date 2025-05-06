import re
from datetime import datetime
from models import db, NoHitter, Team, Person, NoHitterPitcher
from app import app

def parse_no_hitter_lines(pitcher_line, game_line):
    # Find the last date in the pitcher line
    # Accepts: Jan, Jan., February, Feb, Feb., Mar, Mar., etc. (with or without period)
    date_matches = list(re.finditer(r'([A-Z][a-z]+\.?|Sept\.?|Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Jan\.?|Feb\.?|Oct\.?|Nov\.?|Dec\.?|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}', pitcher_line))
    if not date_matches:
        print(f"DEBUG: No date found in pitcher_line: {pitcher_line}")
        return None
    date_str = date_matches[-1].group(0)
    # Normalize 'Sept.' and 'Sept' to 'Sep.' and 'Sep'
    date_str = date_str.replace('Sept.', 'Sep.').replace('Sept', 'Sep')
    # Try parsing with and without period
    try:
        date = datetime.strptime(date_str, '%b. %d, %Y').date()
    except ValueError:
        try:
            date = datetime.strptime(date_str, '%b %d, %Y').date()
        except ValueError:
            try:
                date = datetime.strptime(date_str, '%B %d, %Y').date()
            except ValueError:
                print(f"DEBUG: Date parse error for '{date_str}' in pitcher_line: {pitcher_line}")
                return None
    # Everything before the date is pitcher names
    pitcher_part = pitcher_line[:date_matches[-1].start()].strip().rstrip(',')
    # Split on commas and 'and'
    pitcher_names = re.split(r', | and ', pitcher_part)
    pitcher_names = [p.split('(')[0].strip() for p in pitcher_names if p.strip()]
    # Remove extra info in parentheses from game_line for parsing
    clean_game_line = re.sub(r'\([^)]*\)', '', game_line).strip()
    # Find the last comma (before the score)
    last_comma = clean_game_line.rfind(',')
    if last_comma == -1:
        # Fallback: try to split on the last space for the score
        last_space = clean_game_line.rfind(' ')
        if last_space == -1:
            print(f"DEBUG: No comma or space found in clean_game_line: {clean_game_line}")
            print(f"  pitcher_line: {pitcher_line}")
            print(f"  game_line: {game_line}")
            return None
        teams_part = clean_game_line[:last_space]
        score = clean_game_line[last_space+1:].strip()
    else:
        teams_part = clean_game_line[:last_comma]
        score = clean_game_line[last_comma+1:].strip()
    # Accept 'vs.', 'vs', 'at' as separators
    if ' vs. ' in teams_part:
        team1, team2 = teams_part.split(' vs. ')
        vs_at = 'vs.'
    elif ' vs ' in teams_part:
        team1, team2 = teams_part.split(' vs ')
        vs_at = 'vs'
    elif ' at ' in teams_part:
        team1, team2 = teams_part.split(' at ')
        vs_at = 'at'
    else:
        print(f"DEBUG: No 'vs.', 'vs', or 'at' found in teams_part: {teams_part}")
        print(f"  pitcher_line: {pitcher_line}")
        print(f"  game_line: {game_line}")
        print(f"  clean_game_line: {clean_game_line}")
        print(f"  teams_part: {teams_part}")
        return None
    team1 = team1.strip()
    team2 = team2.strip()
    if vs_at in ['vs.', 'vs']:
        team = team1
        opponent = team2
    else:
        team = team2
        opponent = team1
    # Check for perfect game
    is_pg = '(PG)' in pitcher_line or '(PG)' in game_line
    return {
        'pitchers': pitcher_names,
        'date': date,
        'team': team,
        'opponent': opponent,
        'score': score,
        'is_perfect_game': is_pg
    }

def get_or_create_team(name):
    # Map team names to their Lahman database equivalents
    team_mapping = {
        'D-backs': 'Arizona Diamondbacks',
        'Colt .45s': 'Houston Colt .45\'s',
        'Superbas': 'Brooklyn Superbas',
        'Robins': 'Brooklyn Robins',
        'Bees': 'Boston Bees',
        'Browns': 'St. Louis Browns',
        'Naps': 'Cleveland Naps',
        'Highlanders': 'New York Highlanders',
        'Americans': 'Boston Americans',
        'Terriers': 'Brooklyn Tip-Tops',
        'Whales': 'Chicago Whales',
        'Rebels': 'Pittsburgh Rebels',
        'Packers': 'Buffalo Packers',
        'Blues': 'Buffalo Blues',
        'Tip-Tops': 'Brooklyn Tip-Tops',
        'Grooms': 'Brooklyn Grooms',
        'Spiders': 'Cleveland Spiders',
        'Colonels': 'Louisville Colonels',
        'Beaneaters': 'Boston Beaneaters',
        'Bridegrooms': 'Brooklyn Bridegrooms',
        'Orphans': 'Chicago Orphans',
        'Senators': 'Washington Senators',
        'Dark Blues': 'Hartford Dark Blues',
        'Ruby Legs': 'Worcester Ruby Legs',
        'Grays': 'Providence Grays',
        'White Stockings': 'Chicago White Stockings',
        'Red Stockings': 'Cincinnati Red Stockings',
        'Blue Stockings': 'Cincinnati Blue Stockings',
        'Metropolitans': 'New York Metropolitans',
        'Cowboys': 'New York Cowboys',
        'Buckeyes': 'Columbus Buckeyes',
        'Alleghenys': 'Pittsburgh Alleghenys',
        'Quakers': 'Philadelphia Quakers',
        'Eclipse': 'Louisville Eclipse',
        'Bisons': 'Buffalo Bisons',
        'Stars': 'Syracuse Stars',
        'Broncos': 'Syracuse Broncos',
        # Modern team nicknames
        'Cubs': 'Chicago Cubs',
        'Reds': 'Cincinnati Reds',
        'Nationals': 'Washington Nationals',
        'Astros': 'Houston Astros',
        'Phillies': 'Philadelphia Phillies',
        'Tigers': 'Detroit Tigers',
        'Athletics': 'Oakland Athletics',
        'Yankees': 'New York Yankees',
        'Angels': 'Los Angeles Angels',
        'Mets': 'New York Mets',
        'Brewers': 'Milwaukee Brewers',
        'Dodgers': 'Los Angeles Dodgers',
        'Rangers': 'Texas Rangers',
        'Mariners': 'Seattle Mariners',
        'Indians': 'Cleveland Indians',
        'White Sox': 'Chicago White Sox',
        'Blue Jays': 'Toronto Blue Jays',
        'Twins': 'Minnesota Twins',
        'Rays': 'Tampa Bay Rays',
        'Marlins': 'Miami Marlins',
        'Padres': 'San Diego Padres',
        'Pirates': 'Pittsburgh Pirates',
        'Giants': 'San Francisco Giants',
        'Braves': 'Atlanta Braves',
        'Cardinals': 'St. Louis Cardinals',
        'Expos': 'Montreal Expos',
        'Royals': 'Kansas City Royals',
        'Orioles': 'Baltimore Orioles',
        'Red Sox': 'Boston Red Sox',
        'Rockies': 'Colorado Rockies'
    }
    
    # Look up team in Lahman database by team name
    team = Team.query.filter_by(team_name=name).order_by(Team.yearID.desc()).first()
    if not team:
        # Try mapped name
        mapped_name = team_mapping.get(name)
        if mapped_name:
            team = Team.query.filter_by(team_name=mapped_name).order_by(Team.yearID.desc()).first()
        if not team:
            # Try partial match
            team = Team.query.filter(Team.team_name.like(f"%{name}%")).order_by(Team.yearID.desc()).first()
            if not team:
                print(f"Warning: Team '{name}' not found in Lahman database")
                return None
    return team

def get_or_create_player(full_name):
    # Map player names to their Lahman database equivalents
    player_mapping = {
        'Happy Jack Stivetts': 'Jack Stivetts',
        'Old Hoss Radbourne': 'Charles Radbourn',
        'Big Jeff Pfeffer': 'Jeff Pfeffer',
        'Smoky Joe Wood': 'Joe Wood',
        'Dutch Leonard': 'Hubert Leonard',
        'Bumpus Jones': 'Charles Jones',
        'Ledell Titcomb': 'Ledell Titcomb',
        'Adonis Terry': 'Adonis Terry',
        'Al Atkinson': 'Al Atkinson',
        'Ed Cushman': 'Ed Cushman',
        'Frank Mountain': 'Frank Mountain',
        'Ed Morris': 'Ed Morris',
        'Hugh Daily': 'Hugh Daily',
        'Guy Hecker': 'Guy Hecker',
        'Tony Mullane': 'Tony Mullane',
        'Monte Ward': 'John Ward',
        'Lee Richmond': 'Lee Richmond',
        'George Bradley': 'George Bradley'
    }
    
    # Split name into first and last
    name_parts = full_name.split()
    if len(name_parts) < 2:
        print(f"Warning: Invalid player name format: {full_name}")
        return None
        
    first = name_parts[0]
    last = name_parts[-1]
    
    # Look up player in Lahman database
    try:
        # First try exact match
        person = Person.query.filter_by(nameFirst=first, nameLast=last).first()
        if not person:
            # Try with mapped name if available
            mapped_name = player_mapping.get(full_name)
            if mapped_name:
                first, last = mapped_name.split()
                person = Person.query.filter_by(nameFirst=first, nameLast=last).first()
            if not person:
                # Try partial match on last name
                person = Person.query.filter(Person.nameLast.like(f"%{last}%")).first()
            if not person:
                # Generate Lahman-style playerID
                def make_playerid(first, last, num):
                    return f"{last[:5].lower()}{first[:2].lower()}{num:02d}"
                
                # Find next available number
                num = 1
                playerID = make_playerid(first, last, num)
                while Person.query.filter_by(playerID=playerID).first():
                    num += 1
                    playerID = make_playerid(first, last, num)
                
                print(f"Adding missing player '{full_name}' to database with playerID '{playerID}'.")
                person = Person(playerID=playerID, nameFirst=first, nameLast=last)
                db.session.add(person)
                
        return person
    except Exception as e:
        print(f"Error looking up player {full_name}: {str(e)}")
        return None

def import_no_hitters_from_file(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    missing_teams = set()
    # Process in pairs
    for i in range(0, len(lines), 2):
        if i+1 >= len(lines):
            continue
        pitcher_line = lines[i]
        game_line = lines[i+1]
        data = parse_no_hitter_lines(pitcher_line, game_line)
        if not data:
            print(f"Could not parse: {pitcher_line}\n{game_line}")
            continue
        
        # Get all pitchers
        pitchers = []
        for idx, pitcher_name in enumerate(data['pitchers']):
            pitcher = get_or_create_player(pitcher_name)
            if not pitcher:
                print(f"Skipping no-hitter due to missing pitcher: {pitcher_name}")
                continue
            pitchers.append((pitcher, idx == 0))  # Tuple of (pitcher, is_primary)
        
        if not pitchers:
            continue
            
        team = get_or_create_team(data['team'])
        if not team:
            print(f"Skipping no-hitter due to missing team: {data['team']}")
            missing_teams.add(data['team'])
            continue
            
        opponent = get_or_create_team(data['opponent'])
        if not opponent:
            print(f"Skipping no-hitter due to missing opponent: {data['opponent']}")
            missing_teams.add(data['opponent'])
            continue
            
        # Create the no-hitter record
        no_hitter = NoHitter(
            date=data['date'],
            team=data['team'],
            opponent=data['opponent'],
            score=data['score'],
            is_perfect_game=data['is_perfect_game'],
            team_id=team.teams_ID,
            opponent_team_id=opponent.teams_ID
        )
        db.session.add(no_hitter)
        db.session.flush()  # Get the no_hitter.id
        
        # Create pitcher records
        for pitcher, is_primary in pitchers:
            pitcher_record = NoHitterPitcher(
                no_hitter_id=no_hitter.id,
                player_id=pitcher.playerID,
                is_primary=is_primary
            )
            db.session.add(pitcher_record)
            
    db.session.commit()
    if missing_teams:
        print("\nTeams not found in Lahman database:")
        for t in sorted(missing_teams):
            print(f"  {t}")

if __name__ == '__main__':
    with app.app_context():
        import_no_hitters_from_file('no_hitters.txt') 