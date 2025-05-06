import random
from models import db, NoHitter, NoHitterPitcher, Player
from sqlalchemy.sql import func

def generate_no_hitter_question_mc():
    # Step 1: Get no-hitter IDs with only 1 pitcher
    solo_nhs = (
        db.session.query(NoHitterPitcher.no_hitter_id)
        .group_by(NoHitterPitcher.no_hitter_id)
        .having(func.count(NoHitterPitcher.pitcher_id) == 1)
        .all()
    )
    if not solo_nhs:
        raise ValueError("No solo no-hitters found in DB.")

    nh_id = random.choice(solo_nhs)[0]
    nh = NoHitter.query.get(nh_id)
    pitcher_link = NoHitterPitcher.query.filter_by(no_hitter_id=nh_id).first()
    pitcher = Player.query.get(pitcher_link.pitcher_id)

    correct_name = f"{pitcher.first_name} {pitcher.last_name}"

    # Step 2: Get 3 random incorrect player names
    all_players = (
        db.session.query(Player)
        .filter(Player.id != pitcher.id)
        .all()
    )

    wrong_names = random.sample(
        [f"{p.first_name} {p.last_name}" for p in all_players if p.first_name and p.last_name],
        k=3
    )

    # Step 3: Shuffle options
    options = wrong_names + [correct_name]
    random.shuffle(options)

    # Step 4: Format question
    date_str = nh.date.strftime("%B %-d, %Y")
    question_text = f"Who pitched the no-hitter on {date_str}?"

    # Optional SQL
    raw_sql = f"""
        SELECT p.first_name, p.last_name
        FROM no_hitter_pitcher nhp
        JOIN player p ON p.id = nhp.pitcher_id
        WHERE nhp.no_hitter_id = {nh_id};
    """

    return {
        "question": question_text,
        "options": options,
        "correct_answer": correct_name,
        "sql": raw_sql.strip()
    }
